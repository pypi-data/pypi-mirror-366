"""Paper synthesis functionality for generating literature reviews."""

from dataclasses import dataclass
from litai.database import Database
from litai.llm import LLMClient
from litai.extraction import PaperExtractor, KeyPoint
from litai.models import Paper
from litai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RelevantPaper:
    """A paper deemed relevant to a synthesis query."""

    paper: Paper
    relevance_score: float  # 0-1
    relevance_reason: str
    key_points: list[KeyPoint] | None = None


@dataclass
class SynthesisResult:
    """Result of synthesizing multiple papers."""

    question: str
    synthesis: str
    relevant_papers: list[RelevantPaper]


class PaperSynthesizer:
    """Handles synthesis of multiple papers to answer research questions."""

    def __init__(self, db: Database, llm_client: LLMClient, extractor: PaperExtractor):
        self.db = db
        self.llm = llm_client
        self.extractor = extractor

    async def synthesize(self, question: str) -> SynthesisResult:
        """Generate a synthesis answering the question using papers in library."""
        # Get all papers from library
        papers = self.db.list_papers(limit=100)  # Get more papers for synthesis

        if not papers:
            raise ValueError("No papers in library to synthesize")

        # Step 1: Select relevant papers
        relevant_papers = await self._select_relevant_papers(question, papers)

        if not relevant_papers:
            raise ValueError("No papers found relevant to your question")

        # Step 2: Extract key points from relevant papers
        for rp in relevant_papers:
            try:
                key_points = await self.extractor.extract_key_points(rp.paper.paper_id)
                rp.key_points = key_points
            except Exception as e:
                logger.warning(
                    f"Failed to extract key points from {rp.paper.title}: {e}"
                )
                rp.key_points = []

        # Step 3: Generate synthesis
        synthesis_text = await self._generate_synthesis(question, relevant_papers)

        return SynthesisResult(
            question=question, synthesis=synthesis_text, relevant_papers=relevant_papers
        )

    async def _select_relevant_papers(
        self, question: str, papers: list[Paper]
    ) -> list[RelevantPaper]:
        """Use LLM to select papers relevant to the question."""
        # Format papers for LLM
        paper_list = "\n".join(
            [
                f'{i + 1}. "{paper.title}" ({paper.year})\n'
                f"   Authors: {', '.join(paper.authors[:3])}{' et al.' if len(paper.authors) > 3 else ''}\n"
                f"   Abstract: {paper.abstract[:200]}{'...' if len(paper.abstract) > 200 else ''}"
                for i, paper in enumerate(papers)
            ]
        )

        prompt = f"""Given this research question: "{question}"

And these available papers:
{paper_list}

Select the papers most relevant to answering this question. For each relevant paper:
1. Provide the paper number
2. Give a relevance score (0-1, where 1 is highly relevant)
3. Explain why this paper is relevant to the question

Return your analysis in this format:
PAPER: [number]
SCORE: [0-1]
REASON: [explanation]

Select all papers that could contribute to answering the question, even if tangentially relevant."""

        response = await self.llm.complete(prompt, max_tokens=1000)

        # Parse response
        relevant_papers = []
        lines = response["content"].strip().split("\n")
        i = 0

        while i < len(lines):
            if lines[i].strip().startswith("PAPER:"):
                try:
                    # Extract paper number
                    paper_num = int(lines[i].split(":")[1].strip())
                    if 1 <= paper_num <= len(papers):
                        paper = papers[paper_num - 1]

                        # Extract score
                        score = 0.5  # default
                        if i + 1 < len(lines) and lines[i + 1].strip().startswith(
                            "SCORE:"
                        ):
                            try:
                                score = float(lines[i + 1].split(":")[1].strip())
                            except ValueError:
                                pass

                        # Extract reason
                        reason = "Relevant to the research question"  # default
                        if i + 2 < len(lines) and lines[i + 2].strip().startswith(
                            "REASON:"
                        ):
                            reason = lines[i + 2].split(":", 1)[1].strip()

                        relevant_papers.append(
                            RelevantPaper(
                                paper=paper,
                                relevance_score=score,
                                relevance_reason=reason,
                            )
                        )

                        i += 3  # Move past this entry
                        continue
                except (ValueError, IndexError):
                    pass
            i += 1

        # Sort by relevance score
        relevant_papers.sort(key=lambda x: x.relevance_score, reverse=True)

        return relevant_papers

    async def _generate_synthesis(
        self, question: str, relevant_papers: list[RelevantPaper]
    ) -> str:
        """Generate synthesis text from relevant papers and their key points."""
        # Build context from key points
        context_parts = []

        for i, rp in enumerate(relevant_papers, 1):
            if not rp.key_points:
                continue

            context_parts.append(f'Paper [{i}]: "{rp.paper.title}" ({rp.paper.year})')
            context_parts.append(f"Relevance: {rp.relevance_reason}\n")
            context_parts.append("Key Points:")

            for point in rp.key_points[:5]:  # Limit to top 5 points per paper
                context_parts.append(f"- {point.claim}")
                context_parts.append(
                    f'  Evidence: "{point.evidence}" (Section: {point.section})'
                )

            context_parts.append("")  # Empty line between papers

        context = "\n".join(context_parts)

        prompt = f"""Based on the following research question and key points from relevant papers, provide a comprehensive synthesis.

Research Question: {question}

Relevant Papers and Key Points:
{context}

Please provide a synthesis that:
1. Directly answers the research question
2. Integrates findings from multiple papers
3. Uses inline citations like [1], [2] to reference specific papers
4. Highlights agreements and disagreements between papers
5. Identifies any gaps or limitations in the current literature

Synthesis:"""

        response = await self.llm.complete(prompt, max_tokens=1500)

        return response["content"].strip()
