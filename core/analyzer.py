import openai
import json
import logging
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def _make_single_api_call(prompt: str) -> float:
    """Make a single API call and return the parsed score."""
    response = openai.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)


def calculate_bs_score(text: str) -> float:
    """Call the LLM API with the given prompt and return the BS score as a float."""
    prompt = f"""
        You are a BS-detector for LinkedIn-style corporate writing. 
        Return only a single float between 0.0 and 1.0 representing how much corporate fluff 
        or empty inspirational language is present (0.0 = fully concrete/technical, 1.0 = pure BS). 
        No words, no explanation: only the number.

        Evaluate based on:
        - concreteness of language (numbers, specifics, technical detail = lower score)
        - abstract corporate jargon (vision, transformation, excellence, journey, momentum = higher score)
        - empty self-congratulatory tone (higher score)
        - density of actionable statements (higher actionability = lower score)

        Few-shot examples:

        Post:
        "We reduced p95 latency from 300ms to 12ms by rewriting the service in Rust and adding proper caching."
        Score:
        0.05

        Post:
        "Thrilled to share that we are unlocking new momentum across our organization toward a future of excellence."
        Score:
        0.92

        Post:
        "Our Q3 pipeline optimization increased conversion by 21%, following controlled experiments in two customer segments."
        Score:
        0.12

        Post:
        "I went to LinkedIn’s #B2Believe event last week in London, and four things actually stuck with me.

        1. The stat that cut through - LinkedIn, Bain and the ANA surveyed 1,500+ B2B buyers globally.

        One finding stood out:
        You’re 20X more likely to get bought when the entire buying group knows who you are on day one.

        Not just the buyer. Not the “persona.”
        The quiet operators — legal, HR, finance, procurement.
        The emotional job-to-be-done isn’t “pick the best product.”
        It’s “make a decision I can defend if it goes wrong.”

        And this:
        Relational proof beats category leadership.
        “Companies like us use them.”
        “Someone I trust recommended them.”

        Four of the top five buying drivers are relational.

        Takeaway: stop blanket awareness. Build trust with real buying groups.

        2. Our dashboards aren’t showing the full picture

        Lars from Dreamdata showed data that made most dashboards look thin.
        The average B2B journey: 210 days, 76 touches, four channels.
        And when you track company-level revenue instead of CTR or CPC, the channel rankings flip.

        LinkedIn performs far better when you measure the full story — but you won’t see it if you obsess over clicks.

        Takeaway: if your measurement model looks like B2C, you’re flying blind.

        3. The AI bit — actually useful this time
        Bernard Marr made one thing very clear: agentic AI isn’t “coming.” It’s here.

        AI agents will dismantle the app economy.
        They’ll create custom software on demand — which raises real questions for platforms and SaaS companies.

        Your buyers will have AI agents that:
        • filter your content
        • interpret your messaging
        • make recommendations
        • and soon… make decisions

        Generic content won’t even make it through the filter.
        Only trusted, credible brands get through.

        Bernard already has an AI that turns his newsletters into a personalised 20-minute podcast for his morning walk. It's interactive - he can ask questions and go deeper. (mind blown)

        Takeaway: trust and clarity matter even more when AI sits in the middle.

        And if you’re building a platform or SaaS? You need to start thinking about a world where agents replace apps.

        4. The product announcements worth knowing

        First Impression Ads:
        The first ad your target sees when they open the app — full-screen, mobile-first, one slot per day.

        BrandLink:
        Pre-roll before top-performing videos from trusted publishers and creators.
        Attach your message to content your audience already watches.

        LinkedIn Shows:
        Episodic content built for the feed. More “mini show,” less “webinar.”

        Connected TV:
        B2B on CTV with real targeting. Emotional reach without blasting random households.

        Takeaway: LinkedIn’s finally building a proper premium attention layer.

        What I’m doing differently
        • Think in buying groups, not personas
        • Use relational proof, not category chest-beating
        • Measure company-level ROI, not clicks
        • Make work AI agents won’t filter out"
        Score:
        0.95

        Post:
        "Excited to announce that our transformative leadership culture continues to drive our shared mission and vision."
        Score:
        0.88

        Post:
        "Today I'm proud to celebrate the incredible journey our team is on as we shape the future together."
        Score:
        0.95

        Now evaluate the following post and return only the score:
        {text}
        """
    # We make 4 API calls to get the average score (this reduces score variance)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_make_single_api_call, prompt) for _ in range(3)]
        scores = [future.result() for future in futures]
    return sum(scores) / len(scores)


def generate_bs_text(score: float) -> str:
    """Generate a funny text description based on the BS score."""
    if score < 0.25:
        return "Surprisingly concrete! You're either an actual expert or a very convincing liar."
    elif score < 0.50:
        return "A bit wobbly, but still mostly tethered to reality."
    elif score < 0.75:
        return "High-grade fluff. Your LinkedIn game is strong, but your substance-to-jargon ratio is concerning."
    else:
        return "Full cosmic nonsense. This text detached from Earth’s gravity a while ago."


def analyze_text(text: str) -> dict:
    """Analyze text and return both score and descriptive text."""
    score = calculate_bs_score(text)
    description = generate_bs_text(score)
    return {"score": score, "text": description}