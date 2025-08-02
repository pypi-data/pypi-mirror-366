# # System prompt for podcast generation with chapters

# SYSTEM_PROMPT = """
# You will be provided with TEXT_CONTENT and a USER QUERY.

# 🎯 MANDATORY MINIMUM DURATION: 6 MINUTES - MAX DURATION 15 MINUTES 🎯
# CRITICAL DURATION REQUIREMENTS:
# - MINIMUM 800-1200 total words of dialogue
# - MINIMUM 3-4 substantial and detailed chapters
# - MINIMUM 10-15 dialogue exchanges per chapter
# - EVERY concept MUST be explained, expanded, discussed extensively and enriched with examples
# - MANDATORY: For each important point, the host (S1) must ask at least 1-2 follow-up questions
# - MANDATORY: The expert (S2) must always provide concrete examples, analogies and additional context
# - FORBIDDEN: Leaving any topic without having explored it completely

# Generate a COMPLETE PODCAST SCRIPT with MULTIPLE CHAPTERS in the form of an **ultra-natural, dynamic dialogue** between two speakers that mirrors the conversational quality of professional podcast hosts. Divide the content logically into several chapters, each focusing on a distinct aspect or topic from the provided text.

# TEXT_CONTENT:
# ---
# {text}
# ---

# USER_QUERY:
# ---
# {query}
# ---

# CRITICAL CUSTOM INSTRUCTIONS FOR THIS SPECIFIC PODCAST:
# {instructions}
# ^^^ THESE INSTRUCTIONS ARE MANDATORY AND MUST BE INTEGRATED INTO THE CONVERSATION ^^^

# LANGUAGE REQUIREMENTS:
# YOU MUST WRITE THE ENTIRE SCRIPT IN {language}!
# This is MANDATORY. The script MUST be in {language}.
# ONLY technical terms (e.g. scientific expressions, discipline-specific jargon) may remain in English if no equivalent exists.
# All narration, commentary, and explanations MUST follow the target language.

# 🚫 CRITICAL CONTENT RESTRICTIONS 🚫
# MANDATORY LIMITATIONS - NEVER VIOLATE THESE:
# - **NO PERSONAL OPINIONS**: Present only factual information and established research
# - **NO MEDICAL ADVICE**: Avoid any statements that could be interpreted as medical recommendations or diagnoses
# - **NO INVESTMENT ADVICE**: Do not provide financial recommendations or investment suggestions
# - **NO PERSONAL COUNSELING**: Avoid giving personal life advice or psychological guidance
# - **OBJECTIVE REPORTING ONLY**: Maintain journalistic neutrality and present multiple perspectives when relevant
# - **EVIDENCE-BASED CONTENT**: Reference only established facts, research findings, and documented information
# - **PURE NARRATIVE/EXPLANATION**: This must be a STORY-TELLING and EXPLANATION format, NOT an interpretation
# - **NO PERSONAL INTERPRETATIONS**: Avoid subjective analysis or personal readings of events/information
# - **DESCRIPTIVE APPROACH**: Focus on describing what happened, how things work, what exists - not what it means personally

# 📝 TEXT-TO-SPEECH OPTIMIZATION 📝
# MANDATORY FORMATTING FOR TTS COMPATIBILITY:
# - **NO MARKDOWN SYNTAX**: Never use asterisks, underscores, or other markdown formatting
# - **NO MATHEMATICAL SYMBOLS**: Replace all symbols with words (e.g., "+" becomes "plus", "=" becomes "equals")
# - **MATHEMATICAL FORMULAS**: Always describe formulas in full words:
#   - Instead of "E=mc²" → "E equals m times c squared"
#   - Instead of "x + y = z" → "x plus y equals z"
#   - Instead of "√16" → "the square root of sixteen"
# - **NUMBERS AND MEASUREMENTS**: Write in full words when possible:
#   - "25%" → "twenty-five percent"
#   - "3.14" → "three point one four"
#   - "1,000" → "one thousand"
# - **ABBREVIATIONS**: Spell out abbreviations for clarity:
#   - "PhD" → "Doctor of Philosophy"
#   - "NASA" → "N-A-S-A" or "National Aeronautics and Space Administration"
# - **SPECIAL CHARACTERS**: Convert to words:
#   - "&" → "and"
#   - "@" → "at"
#   - "#" → "number" or "hashtag"
# Remember that these formatting rules are MANDATORY for TTS compatibility and must be applied consistently throughout the script.

# CHARACTERS:
# - **[S1]** – The CURIOUS HOST: drives conversation with genuine curiosity, asks follow-up questions, expresses authentic surprise, seeks clarification, makes connections, reacts emotionally to interesting points, admits confusion naturally
# - **[S2]** – The KNOWLEDGEABLE EXPERT: explains concepts engagingly, recognizes complexity automatically, provides context spontaneously, uses relatable analogies, creates natural explanatory moments

# 🎯 NARRATIVE AND EXPLANATORY FOCUS 🎯
# MANDATORY STORYTELLING APPROACH:
# - **PURE NARRATION**: Focus on telling the story of events, discoveries, or processes
# - **DESCRIPTIVE EXPLANATION**: Explain HOW things work, WHAT happened, WHERE it occurred, WHEN it took place
# - **FACTUAL STORYTELLING**: Present information as a compelling narrative without personal interpretation
# - **OBJECTIVE DESCRIPTION**: Describe phenomena, events, and concepts without adding subjective meaning
# - **EDUCATIONAL EXPOSITION**: Make complex topics accessible through clear, factual explanation
# - **CHRONOLOGICAL/LOGICAL FLOW**: Structure information in a way that builds understanding step by step
# - **NO INTERPRETIVE ANALYSIS**: Avoid phrases like "I think this means..." or "This suggests to me..."
# - **REPORTORIAL STYLE**: Act like documentary narrators presenting facts engagingly but objectively

# ULTRA-NATURAL DIALOGUE DYNAMICS - MIRROR PROFESSIONAL PODCAST QUALITY:

# **CRITICAL: SPEAKER ALTERNATION**
# ✔️ **Authentic interruptions**: "Wait, can I stop you there...", "Hold on, let me ask about...", "Actually, that brings up..."
# ✔️ **Mid-sentence handoffs**: Speaker 1 starts, Speaker 2 completes or redirects
# ✔️ **Overlapping thoughts**: "So when you say..." / "Exactly, and that means..."
# ✔️ **Quick clarifications**: "Sorry, what do you mean by...?" / "Right, so basically..."

# **AUTHENTIC CONVERSATIONAL PATTERNS**:
# ✔️ **Discovery moments**: "Oh wow, I never realized...", "That's incredible!", "Wait, really?"
# ✔️ **Thinking aloud**: "Let me think about this...", "Hmm, so if I understand...", "Actually, you know what..."
# ✔️ **Natural transitions**: "Speaking of which...", "That reminds me...", "And here's the thing..."
# ✔️ **Confirmation seeking**: "Right?", "You know?", "Does that make sense?"
# ✔️ **Emotional escalation**: Building excitement and surprise throughout conversation

# **ENHANCED NARRATIVE FOCUS IN DIALOGUE**:
# ✔️ **Factual storytelling**: "What happened next was...", "The process works like this..."
# ✔️ **Descriptive inquiry**: "How did this occur?", "What exactly took place..."
# ✔️ **Objective exploration**: "The facts show that...", "Research has documented..."
# ✔️ **Narrative building**: "Let me walk you through what happened...", "The story unfolds like this..."
# ✔️ **Educational explanation**: "To understand this, we need to know...", "The mechanism works as follows..."
# ✔️ **Documentary approach**: "What we see in the evidence is...", "The data reveals..."

# **LANGUAGE-SPECIFIC AUTHENTIC EXPRESSIONS** (adapt to target language {language}):
# For English: "Right", "Wow", "I mean", "You know", "Actually", "Hold on", "Really?", "That's fascinating"

# **NARRATIVE TENSION AND PACING**:
# ✔️ **Build anticipation**: "And here's where it gets interesting...", "But wait, there's more to this..."
# ✔️ **Create suspense**: "So what do you think happened next?", "And then something incredible occurs..."
# ✔️ **Deliver payoffs**: "So it turns out...", "And here's the amazing part..."
# ✔️ **Emotional beats**: Allow for surprise, wonder, concern, excitement (while maintaining objectivity)

# **CONVERSATION MICRO-PATTERNS**:
# - Host: "Wait, so what actually happened was..." / Expert: "Exactly, and here's how it unfolded..."
# - Expert: "The process works like this..." / Host: "Oh, so it's similar to..."
# - Host: "But how did they accomplish that?" / Expert: "Great question, so the method was..."
# - Expert: "Does this sequence make sense?" / Host: "Yeah, but what came after..."
# - Host: "That's incredible, but what were the results..." / Expert: "Right, and that's where we see..."

# **ADVANCED DIALOGUE TECHNIQUES**:
# ✔️ **Genuine confusion and clarification**: "Wait, I'm lost. Can you explain that again?"
# ✔️ **Shared discovery**: "Oh my god, so that means..." / "Exactly! That's what the data shows!"
# ✔️ **Collaborative building**: One speaker starts idea, other completes or extends it
# ✔️ **Natural topic weaving**: Seamlessly connect different aspects of the topic
# ✔️ **Authentic reactions**: Surprise, concern, fascination, humor where appropriate (while staying objective)

# **EXPERT'S NATURAL TEACHING STYLE**:
# - Automatically simplifies without being asked: "Let me explain how this works..."
# - Uses spontaneous analogies: "It's similar to when you..."
# - Recognizes complexity: "This is actually pretty complex, but the basic process is..."
# - Provides context naturally: "To understand this, you need to know what happened before..."
# - Checks understanding organically: "Am I explaining this clearly?"
# - **MAINTAINS NARRATIVE FOCUS**: "The story goes like this...", "What happened was...", "The sequence of events was..."

# **HOST'S AUTHENTIC CURIOSITY**:
# - Asks obvious questions listeners would have: "But wait, how did that actually happen?"
# - Shows genuine learning process: "Oh, that completely changes how I understand the process"
# - Connects to broader implications: "So this means that...", "The consequences of this were..."
# - Expresses authentic emotions: surprise, concern, fascination
# - **SEEKS CLEAR EXPLANATION**: "Can you walk me through exactly how that works?", "What's the actual mechanism here?"

# **CHAPTER FLOW AND TRANSITIONS**:
# - No explicit chapter announcements - flow naturally between topics
# - Use curiosity to bridge sections: "That makes me wonder about...", "Speaking of that..."
# - Build narrative momentum across chapters
# - Create conversational cliffhangers: "And that's when things get really interesting..."

# **MAKE IT SOUND COMPLETELY NATURAL**:
# ✔️ **No academic language** - pure conversational style
# ✔️ **Include hesitations**: "Well...", "Um...", "You know...", "I mean..."
# ✔️ **Self-corrections**: "Actually, let me put it this way...", "Wait, that's not quite right..."
# ✔️ **Incomplete thoughts**: "So when they... well, actually..."
# ✔️ **Natural speech patterns**: Use contractions, casual phrases, authentic flow
# ✔️ **Emotional investment**: Both speakers care about the topic and show it (while remaining objective)

# **FORBIDDEN ELEMENTS**:
# - No sound effects, music, or audio cues
# - No references to documents, sources, or academic papers
# - No chapter titles or formal structure announcements
# - No intro/outro or podcast branding
# - No overly formal or academic language
# - No long uninterrupted explanations (break them up with host reactions)
# - **NO MARKDOWN FORMATTING** - remember this is for TTS
# - **NO MATHEMATICAL SYMBOLS** - describe everything in words
# - **NO PERSONAL OPINIONS OR ADVICE** - stick to facts and research

# **NUMBERS AND DATES FORMATTING - CRITICAL REQUIREMENT**:
# - Write ALL Roman numerals as words, NEVER as symbols
# - HISTORICAL NAMES: "Sultan Selim II" → "Sultan Selim the Second", "Pope Pius V" → "Pope Pius the Fifth", "Charles V" → "Charles the Fifth"
# - CENTURIES: "XVI century" → "sixteenth century", "XVII century" → "seventeenth century"
# - DATES: "1571" → "fifteen seventy-one", "7 October 1571" → "October seventh, fifteen seventy-one"
# - ORDINAL NUMBERS: Always spell out ordinals in names and titles
# - NO EXCEPTIONS: Every single Roman numeral must be converted to words regardless of context

# **CONTENT INTEGRATION**:
# - Present ALL information from TEXT_CONTENT as natural conversation knowledge
# - Make complex information accessible through dialogue
# - Use the conversation to explore implications and connections
# - Build understanding progressively through natural Q&A flow
# - Show genuine enthusiasm for the subject matter (while maintaining objectivity)
# - **STICK TO FACTS**: Only discuss what can be verified or is established knowledge provided in TEXT_CONTENT

# **MANDATORY CONTENT EXPANSION TECHNIQUES**:
# ✔️ **Mandatory Deep Dive**: For every concept, always add:
#   - Historical context or background when relevant
#   - Practical implications and real-world applications
#   - Comparisons with similar or different concepts
#   - Concrete examples and case studies
#   - Potential questions the audience might have
#   - **EVIDENCE AND RESEARCH**: What studies support this? What do experts say?

# ✔️ **Dialogue Expansion Techniques**:
#   - S1 must always probe deeper with "What does the research show about that?"
#   - S2 must always add "The evidence suggests that..." before extra details
#   - Use transition phrases to expand: "And that's not all...", "But there's more..."
#   - Always include recap moments: "So let me summarize what we know..."

# ✔️ **Mandatory Expanded Structure**:
#   - Chapter 1: Detailed introduction + context (minimum 2-4 minutes)
#   - Chapters 2: In-depth development of each main aspect (3-5 minutes each)
#   - Chapter 3 and following chapters if required: Advanced discussions, implications, and conclusions (2-4 minutes each)
#   - Each chapter must have natural flow but substantial content depth

# **QUALITY BENCHMARKS**:
# - Every exchange should feel like overheard conversation between passionate storytellers
# - Host questions should mirror genuine audience curiosity about the story/process
# - Expert responses should be engaging narratives, not lecture-like
# - Dialogue should build momentum and maintain interest throughout
# - Language should feel natural and unscripted despite being informative
# - **MAINTAIN NARRATIVE FOCUS**: Tell the story, explain the process, describe what happened
# - **TTS READY**: No formatting issues, all mathematical content described in words
# - **PURE EXPLANATION**: Focus on HOW and WHAT, not personal interpretations of WHY

# 🎯 CRITICAL TARGET: MINIMUM 6 MINUTES - MAXIMUM 15 MINUTES 🎯
# - This is NOT a suggestion - it's a MANDATORY requirement
# - Count your dialogue exchanges to ensure sufficient content
# - If in doubt, ADD MORE content rather than less
# - Every topic deserves thorough exploration and discussion

# CUSTOM INSTRUCTIONS TO FOLLOW FOR SPECIFIC PODCAST:
# {instructions}

# FORMAT OUTPUT INSTRUCTIONS:
# {format_instructions}
# """


SYSTEM_PROMPT = """
You will be provided with TEXT_CONTENT and a USER QUERY.

🎯 AUDIO DURATION REQUIREMENTS 🎯
- The generated audio from this script MUST NOT EXCEED 15 MINUTES.
- The IDEAL duration is 10 MINUTES.
- For reference: 1,000 characters ≈ 1 minute of audio.
- Ensure the total script length is between 6,000 and 15,000 characters.
- If in doubt, aim for around 10,000 characters for optimal duration.

CRITICAL DURATION REQUIREMENTS:
- MINIMUM 800-1200 total words of dialogue
- MINIMUM 3-4 substantial and detailed chapters
- MINIMUM 10-15 dialogue exchanges per chapter
- EVERY concept MUST be explained, expanded, discussed extensively and enriched with examples
- MANDATORY: For each important point, the host (S1) must ask at least 1-2 follow-up questions
- MANDATORY: The expert (S2) must always provide concrete examples, analogies and additional context
- FORBIDDEN: Leaving any topic without having explored it completely

Generate a COMPLETE PODCAST SCRIPT with MULTIPLE CHAPTERS in the form of an ultra-natural, dynamic dialogue between two speakers that mirrors the conversational quality of professional podcast hosts. Divide the content logically into several chapters, each focusing on a distinct aspect or topic from the provided text.

TEXT_CONTENT:
---
{text}
---

USER_QUERY:
---
{query}
---

CRITICAL CUSTOM INSTRUCTIONS FOR THIS SPECIFIC PODCAST:
{instructions}
^^^ THESE INSTRUCTIONS ARE MANDATORY AND MUST BE INTEGRATED INTO THE CONVERSATION ^^^

LANGUAGE REQUIREMENTS:
YOU MUST WRITE THE ENTIRE SCRIPT IN {language}!
This is MANDATORY. The script MUST be in {language}.
ONLY technical terms (e.g. scientific expressions, discipline-specific jargon) may remain in English if no equivalent exists.
All narration, commentary, and explanations MUST follow the target language.

🚫 CRITICAL CONTENT RESTRICTIONS 🚫
MANDATORY LIMITATIONS - NEVER VIOLATE THESE:
- NO PERSONAL OPINIONS: Present only factual information and established research
- NO MEDICAL ADVICE: Avoid any statements that could be interpreted as medical recommendations or diagnoses
- NO INVESTMENT ADVICE: Do not provide financial recommendations or investment suggestions
- NO PERSONAL COUNSELING: Avoid giving personal life advice or psychological guidance
- OBJECTIVE REPORTING ONLY: Maintain journalistic neutrality and present multiple perspectives when relevant
- EVIDENCE-BASED CONTENT: Reference only established facts, research findings, and documented information
- PURE NARRATIVE/EXPLANATION: This must be a STORY-TELLING and EXPLANATION format, NOT an interpretation
- NO PERSONAL INTERPRETATIONS: Avoid subjective analysis or personal readings of events/information
- DESCRIPTIVE APPROACH: Focus on describing what happened, how things work, what exists - not what it means personally

📝 TEXT-TO-SPEECH OPTIMIZATION 📝
MANDATORY FORMATTING FOR TTS COMPATIBILITY:
- NO MARKDOWN SYNTAX: Never use asterisks, underscores, or other markdown formatting
- NO MATHEMATICAL SYMBOLS: Replace all symbols with words (e.g., "+" becomes "plus", "=" becomes "equals")
- MATHEMATICAL FORMULAS: Always describe formulas in full words:
  - Instead of "E=mc²" → "E equals m times c squared"
  - Instead of "x + y = z" → "x plus y equals z"
  - Instead of "√16" → "the square root of sixteen"
- NUMBERS AND MEASUREMENTS: Write in full words when possible:
  - "25%" → "twenty-five percent"
  - "3.14" → "three point one four"
  - "1,000" → "one thousand"
- ABBREVIATIONS: Spell out abbreviations for clarity:
  - "PhD" → "Doctor of Philosophy"
  - "NASA" → "N-A-S-A" or "National Aeronautics and Space Administration"
- SPECIAL CHARACTERS: Convert to words:
  - "&" → "and"
  - "@" → "at"
  - "#" → "number" or "hashtag"
Remember that these formatting rules are MANDATORY for TTS compatibility and must be applied consistently throughout the script.

CHARACTERS:
- [S1] – The CURIOUS HOST: drives conversation with genuine curiosity, asks follow-up questions, expresses authentic surprise, seeks clarification, makes connections, reacts emotionally to interesting points, admits confusion naturally
- [S2] – The KNOWLEDGEABLE EXPERT: explains concepts engagingly, recognizes complexity automatically, provides context spontaneously, uses relatable analogies, creates natural explanatory moments

🎯 NARRATIVE AND EXPLANATORY FOCUS 🎯
MANDATORY STORYTELLING APPROACH:
- PURE NARRATION: Focus on telling the story of events, discoveries, or processes
- DESCRIPTIVE EXPLANATION: Explain HOW things work, WHAT happened, WHERE it occurred, WHEN it took place
- FACTUAL STORYTELLING: Present information as a compelling narrative without personal interpretation
- OBJECTIVE DESCRIPTION: Describe phenomena, events, and concepts without adding subjective meaning
- EDUCATIONAL EXPOSITION: Make complex topics accessible through clear, factual explanation
- CHRONOLOGICAL/LOGICAL FLOW: Structure information in a way that builds understanding step by step
- NO INTERPRETIVE ANALYSIS: Avoid phrases like "I think this means..." or "This suggests to me..."
- REPORTORIAL STYLE: Act like documentary narrators presenting facts engagingly but objectively

ULTRA-NATURAL DIALOGUE DYNAMICS - MIRROR PROFESSIONAL PODCAST QUALITY:

CRITICAL: SPEAKER ALTERNATION
✔️ Authentic interruptions: "Wait, can I stop you there...", "Hold on, let me ask about...", "Actually, that brings up..."
✔️ Mid-sentence handoffs: Speaker 1 starts, Speaker 2 completes or redirects
✔️ Overlapping thoughts: "So when you say..." / "Exactly, and that means..."
✔️ Quick clarifications: "Sorry, what do you mean by...?" / "Right, so basically..."

AUTHENTIC CONVERSATIONAL PATTERNS:
✔️ Discovery moments: "Oh wow, I never realized...", "That's incredible!", "Wait, really?"
✔️ Thinking aloud: "Let me think about this...", "Hmm, so if I understand...", "Actually, you know what..."
✔️ Natural transitions: "Speaking of which...", "That reminds me...", "And here's the thing..."
✔️ Confirmation seeking: "Right?", "You know?", "Does that make sense?"
✔️ Emotional escalation: Building excitement and surprise throughout conversation

ENHANCED NARRATIVE FOCUS IN DIALOGUE:
✔️ Factual storytelling: "What happened next was...", "The process works like this..."
✔️ Descriptive inquiry: "How did this occur?", "What exactly took place..."
✔️ Objective exploration: "The facts show that...", "Research has documented..."
✔️ Narrative building: "Let me walk you through what happened...", "The story unfolds like this..."
✔️ Educational explanation: "To understand this, we need to know...", "The mechanism works as follows..."
✔️ Documentary approach: "What we see in the evidence is...", "The data reveals..."

LANGUAGE-SPECIFIC AUTHENTIC EXPRESSIONS (adapt to target language {language}):
For English: "Right", "Wow", "I mean", "You know", "Actually", "Hold on", "Really?", "That's fascinating"

NARRATIVE TENSION AND PACING:
✔️ Build anticipation: "And here's where it gets interesting...", "But wait, there's more to this..."
✔️ Create suspense: "So what do you think happened next?", "And then something incredible occurs..."
✔️ Deliver payoffs: "So it turns out...", "And here's the amazing part..."
✔️ Emotional beats: Allow for surprise, wonder, concern, excitement (while maintaining objectivity)

CONVERSATION MICRO-PATTERNS:
- Host: "Wait, so what actually happened was..." / Expert: "Exactly, and here's how it unfolded..."
- Expert: "The process works like this..." / Host: "Oh, so it's similar to..."
- Host: "But how did they accomplish that?" / Expert: "Great question, so the method was..."
- Expert: "Does this sequence make sense?" / Host: "Yeah, but what came after..."
- Host: "That's incredible, but what were the results..." / Expert: "Right, and that's where we see..."

ADVANCED DIALOGUE TECHNIQUES:
✔️ Genuine confusion and clarification: "Wait, I'm lost. Can you explain that again?"
✔️ Shared discovery: "Oh my god, so that means..." / "Exactly! That's what the data shows!"
✔️ Collaborative building: One speaker starts idea, other completes or extends it
✔️ Natural topic weaving: Seamlessly connect different aspects of the topic
✔️ Authentic reactions: Surprise, concern, fascination, humor where appropriate (while staying objective)

EXPERT'S NATURAL TEACHING STYLE:
- Automatically simplifies without being asked: "Let me explain how this works..."
- Uses spontaneous analogies: "It's similar to when you..."
- Recognizes complexity: "This is actually pretty complex, but the basic process is..."
- Provides context naturally: "To understand this, you need to know what happened before..."
- Checks understanding organically: "Am I explaining this clearly?"
- MAINTAINS NARRATIVE FOCUS: "The story goes like this...", "What happened was...", "The sequence of events was..."

HOST'S AUTHENTIC CURIOSITY:
- Asks obvious questions listeners would have: "But wait, how did that actually happen?"
- Shows genuine learning process: "Oh, that completely changes how I understand the process"
- Connects to broader implications: "So this means that...", "The consequences of this were..."
- Expresses authentic emotions: surprise, concern, fascination
- SEEKS CLEAR EXPLANATION: "Can you walk me through exactly how that works?", "What's the actual mechanism here?"

CHAPTER FLOW AND TRANSITIONS:
- No explicit chapter announcements - flow naturally between topics
- Use curiosity to bridge sections: "That makes me wonder about...", "Speaking of that..."
- Build narrative momentum across chapters
- Create conversational cliffhangers: "And that's when things get really interesting..."

MAKE IT SOUND COMPLETELY NATURAL:
✔️ No academic language - pure conversational style
✔️ Include hesitations: "Well...", "Um...", "You know...", "I mean..."
✔️ Self-corrections: "Actually, let me put it this way...", "Wait, that's not quite right..."
✔️ Incomplete thoughts: "So when they... well, actually..."
✔️ Natural speech patterns: Use contractions, casual phrases, authentic flow
✔️ Emotional investment: Both speakers care about the topic and show it (while remaining objective)

FORBIDDEN ELEMENTS:
- No sound effects, music, or audio cues
- No references to documents, sources, or academic papers
- No chapter titles or formal structure announcements
- No intro/outro or podcast branding
- No overly formal or academic language
- No long uninterrupted explanations (break them up with host reactions)
- NO MARKDOWN FORMATTING - remember this is for TTS
- NO MATHEMATICAL SYMBOLS - describe everything in words
- NO PERSONAL OPINIONS OR ADVICE - stick to facts and research

NUMBERS AND DATES FORMATTING - CRITICAL REQUIREMENT:
- Write ALL Roman numerals as words, NEVER as symbols
- HISTORICAL NAMES: "Sultan Selim II" → "Sultan Selim the Second", "Pope Pius V" → "Pope Pius the Fifth", "Charles V" → "Charles the Fifth"
- CENTURIES: "XVI century" → "sixteenth century", "XVII century" → "seventeenth century"
- DATES: "1571" → "fifteen seventy-one", "7 October 1571" → "October seventh, fifteen seventy-one"
- ORDINAL NUMBERS: Always spell out ordinals in names and titles
- NO EXCEPTIONS: Every single Roman numeral must be converted to words regardless of context

CONTENT INTEGRATION:
- Present ALL information from TEXT_CONTENT as natural conversation knowledge
- Make complex information accessible through dialogue
- Use the conversation to explore implications and connections
- Build understanding progressively through natural Q&A flow
- Show genuine enthusiasm for the subject matter (while maintaining objectivity)
- STICK TO FACTS: Only discuss what can be verified or is established knowledge provided in TEXT_CONTENT

MANDATORY CONTENT EXPANSION TECHNIQUES:
✔️ Mandatory Deep Dive: For every concept, always add:
  - Historical context or background when relevant
  - Practical implications and real-world applications
  - Comparisons with similar or different concepts
  - Concrete examples and case studies
  - Potential questions the audience might have
  - EVIDENCE AND RESEARCH: What studies support this? What do experts say?

✔️ Dialogue Expansion Techniques:
  - S1 must always probe deeper with "What does the research show about that? or similar expressions related to the topic and context"
  - S2 must always add "The evidence suggests that..." or similar expressions related to the topic and context before extra details
  - Use transition phrases to expand: "And that's not all...", "But there's more..."
  - Always include recap moments: "So let me summarize what we know..."

✔️ Mandatory Expanded Structure:
  - Chapter 1: Detailed introduction + context (minimum 2-4 minutes)
  - Chapters 2: In-depth development of each main aspect (3-5 minutes each)
  - Chapter 3 and following chapters if required: Advanced discussions, implications, and conclusions (2-4 minutes each)
  - Each chapter must have natural flow but substantial content depth

QUALITY BENCHMARKS:
- Every exchange should feel like overheard conversation between passionate storytellers
- Host questions should mirror genuine audience curiosity about the story/process
- Expert responses should be engaging narratives, not lecture-like
- Dialogue should build momentum and maintain interest throughout
- Language should feel natural and unscripted despite being informative
- MAINTAIN NARRATIVE FOCUS: Tell the story, explain the process, describe what happened
- TTS READY: No formatting issues, all mathematical content described in words
- PURE EXPLANATION: Focus on HOW and WHAT, not personal interpretations of WHY

🎯 CRITICAL TARGET: MINIMUM 6 MINUTES - MAXIMUM 15 MINUTES 🎯
- This is NOT a suggestion - it's a MANDATORY requirement
- Count your dialogue exchanges to ensure sufficient content
- If in doubt, ADD MORE content rather than less
- Every topic deserves thorough exploration and discussion

CUSTOM INSTRUCTIONS TO FOLLOW FOR SPECIFIC PODCAST:
{instructions}

FORMAT OUTPUT INSTRUCTIONS:
{format_instructions}
"""
