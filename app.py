import streamlit as st
import json
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="What Are You Really Grieving in Your Divorce?",
    page_icon="💔",
    layout="wide"
)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Force reset admin mode for public users
st.session_state.admin_mode = False

# Grief Quiz Questions
QUESTIONS = [
    {
        "id": "initiate",
        "question": "Who initiated the divorce?",
        "options": [
            ("A", "I did, I knew it was time to leave."),
            ("B", "My spouse did, I didn't want it to end."),
            ("C", "It was mutual, or we drifted apart."),
            ("D", "It's complicated, there's no clear answer.")
        ]
    },
    {
        "id": "feelings",
        "question": "What's the hardest part of your divorce right now?",
        "options": [
            ("A", "Figuring out who I am without my relationship."),
            ("B", "The emotional roller-coaster and heartbreak."),
            ("C", "Managing all the practical stuff and money stress."),
            ("D", "Worrying about my kids and their stability.")
        ]
    },
    {
        "id": "current_truth",
        "question": "Which of these statements feels most true right now?",
        "options": [
            ("A", "I miss my home and the neighborhood I once had."),
            ("B", "I still think about my ex and feel heartbroken."),
            ("C", "I'm grieving the family life I thought I was giving my kids."),
            ("D", "I don't even recognize myself anymore.")
        ]
    },
    {
        "id": "future_hard",
        "question": "When you imagine your future, what's the hardest part?",
        "options": [
            ("A", "Imagining doing life without a partner."),
            ("B", "Figuring out who I'll be on my own."),
            ("C", "Planning around parenting schedules and time with my kids."),
            ("D", "Worrying about affording the life I want.")
        ]
    },
    {
        "id": "daily_change",
        "question": "What's the biggest change that's impacted your day-to-day life?",
        "options": [
            ("A", "The silence or loneliness without my ex."),
            ("B", "The instability of parenting alone or on a schedule."),
            ("C", "Managing money, housing, or legal stuff on my own."),
            ("D", "The identity shift, not being someone's partner anymore.")
        ]
    },
    {
        "id": "grieve_hidden",
        "question": "What do you grieve that others may not realize?",
        "options": [
            ("A", "Losing myself in that marriage."),
            ("B", "The emotional intimacy I had with my spouse."),
            ("C", "The comforts and routines of our shared lifestyle."),
            ("D", "The family moments that now feel fractured.")
        ]
    },
    {
        "id": "low_thoughts",
        "question": "When you're alone and feeling low, what thought tends to surface?",
        "options": [
            ("A", "I'm not sure I'll ever find love like that again."),
            ("B", "How did I end up in this financial mess?"),
            ("C", "I feel like I failed my kids."),
            ("D", "I don't know who I am without my relationship.")
        ]
    },
    {
        "id": "happy_couples",
        "question": "How do you feel when you see happy couples or families?",
        "options": [
            ("A", "It reminds me of the partner I lost."),
            ("B", "I think about how I miss being part of a unit with my kids."),
            ("C", "I compare their lifestyle to mine and feel the loss."),
            ("D", "It makes me reflect on how far away I feel from that life now.")
        ]
    },
    {
        "id": "telling_people",
        "question": "What's been the hardest part about telling people you're divorced?",
        "options": [
            ("A", "Admitting that life feels less secure now, financially or otherwise."),
            ("B", "Feeling embarrassed that my relationship didn't work out."),
            ("C", "Explaining what it's like to co-parent or not see my kids all the time."),
            ("D", "Trying to explain the emotional toll or loss of direction.")
        ]
    },
    {
        "id": "current_phrase",
        "question": "Which phrase feels most like your current grief?",
        "options": [
            ("A", '"I miss what we had."'),
            ("B", '"I don\'t know how I\'ll ever make ends meet on my own."'),
            ("C", '"I feel like I\'ve let my family fall apart."'),
            ("D", '"I don\'t know who I am anymore."')
        ]
    },
    {
        "id": "friendships_grief",
        "question": "Have you experienced grief over friendships, community, or routines that disappeared?",
        "options": [
            ("A", "Yes, losing those connections was almost as hard as the divorce."),
            ("B", "A little, some relationships faded, but I expected that."),
            ("C", "No, my circle stayed strong."),
            ("D", "I didn't notice until recently, and now it's hitting me.")
        ]
    },
    {
        "id": "least_understood",
        "question": "When people try to comfort you, what feels least understood?",
        "options": [
            ("A", "That I still love the person I left (or who left me)."),
            ("B", "That I'm not just grieving a person, I'm grieving stability."),
            ("C", "That I feel broken about what this means for my kids."),
            ("D", "That I don't recognize my life or identity anymore.")
        ]
    },
    {
        "id": "symptoms",
        "question": "What physical or emotional symptom do you notice most?",
        "options": [
            ("A", "Heartache over the loss of my relationship with my spouse."),
            ("B", "Feelings of depression tied to how I see my role as a spouse or parent."),
            ("C", "Anxiety about managing finances and paying bills on my own."),
            ("D", "Sadness about my identity as \"just another divorced person.\"")
        ]
    }
]

def save_user_response(user_id, responses, email=""):
    """Save user responses to a JSON file for admin tracking"""
    data_file = "user_responses.json"
    
    # Load existing data or create new
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = {}
    
    # Calculate grief scores
    scores = calculate_grief_scores(responses)
    
    # Add current user's data
    all_data[user_id] = {
        "email": email,
        "responses": responses,
        "scores": scores,
        "timestamp": datetime.now().isoformat(),
        "completed": True
    }
    
    # Save back to file
    with open(data_file, 'w') as f:
        json.dump(all_data, f, indent=2)

def load_all_responses():
    """Load all user responses for admin view"""
    data_file = "user_responses.json"
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return {}

def calculate_grief_scores(responses):
    """Calculate grief type scores based on responses"""
    # Scoring logic - each answer maps to different grief types
    score_map = {
        "initiate": {"A": ["existentialGrief"], "B": ["spousalGrief"], "C": ["spousalGrief"], "D": ["existentialGrief"]},
        "feelings": {"A": ["existentialGrief"], "B": ["spousalGrief"], "C": ["materialGrief"], "D": ["familyGrief"]},
        "current_truth": {"A": ["materialGrief"], "B": ["spousalGrief"], "C": ["familyGrief"], "D": ["existentialGrief"]},
        "future_hard": {"A": ["spousalGrief"], "B": ["existentialGrief"], "C": ["familyGrief"], "D": ["materialGrief"]},
        "daily_change": {"A": ["spousalGrief"], "B": ["familyGrief"], "C": ["materialGrief"], "D": ["existentialGrief"]},
        "grieve_hidden": {"A": ["existentialGrief"], "B": ["spousalGrief"], "C": ["materialGrief"], "D": ["familyGrief"]},
        "low_thoughts": {"A": ["spousalGrief"], "B": ["materialGrief"], "C": ["familyGrief"], "D": ["existentialGrief"]},
        "happy_couples": {"A": ["spousalGrief"], "B": ["familyGrief"], "C": ["materialGrief"], "D": ["existentialGrief"]},
        "telling_people": {"A": ["materialGrief"], "B": ["spousalGrief"], "C": ["familyGrief"], "D": ["existentialGrief"]},
        "current_phrase": {"A": ["spousalGrief"], "B": ["materialGrief"], "C": ["familyGrief"], "D": ["existentialGrief"]},
        "friendships_grief": {"A": ["materialGrief"], "B": ["materialGrief"], "C": ["spousalGrief"], "D": ["existentialGrief"]},
        "least_understood": {"A": ["spousalGrief"], "B": ["materialGrief"], "C": ["familyGrief"], "D": ["existentialGrief"]},
        "symptoms": {"A": ["spousalGrief"], "B": ["familyGrief"], "C": ["materialGrief"], "D": ["existentialGrief"]}
    }
    
    # Initialize scores
    scores = {
        "spousalGrief": 0,
        "materialGrief": 0,
        "familyGrief": 0,
        "existentialGrief": 0
    }
    
    # Calculate scores
    for question_id, answer in responses.items():
        if question_id in score_map and answer in score_map[question_id]:
            for grief_type in score_map[question_id][answer]:
                scores[grief_type] += 1
    
    return scores

def get_grief_interpretation(scores):
    """Get grief type interpretation based on scores"""
    grief_types = {
        "spousalGrief": {
            "title": "Grieving the Loss of the Relationship (Spousal Grief)",
            "description": "You're grieving the emotional connection you once had with your spouse. Whether or not you wanted the divorce, you still feel the loss of love, history, and emotional intimacy. This kind of grief can be especially painful when others assume you \"should be over it.\"",
            "why": "Even if the relationship wasn't healthy or sustainable, emotional bonds don't just disappear. You likely shared years of memories, milestones, and moments of closeness. When that ends, whether by your choice or not, it can feel like a death. You're grieving a person, a bond, and what might have been.",
            "recommendations": [
                "Grief counselling to process complex emotions like love, anger, and longing",
                "Narrative therapy to reframe the relationship and create emotional closure",
                "Knowing it's okay to mourn someone you also needed to leave"
            ]
        },
        "materialGrief": {
            "title": "Grieving the Loss of Financial Security & Lifestyle (Material Grief)",
            "description": "Divorce has disrupted your sense of stability. You may feel anxious or unmoored about money, housing, or what the future looks like. This grief isn't superficial, it's deeply tied to identity, safety, and long-term dreams.",
            "why": "Divorce often dismantles the lifestyle and long-term plans you built together. You may be grieving the loss of financial safety, the home you loved, or the future you were counting on. Maybe you're anxious about how you'll make ends meet on one income. These are more than material losses, they're connected to your sense of identity, freedom, and stability.",
            "recommendations": [
                "Financial coaching and legal support to build new security",
                "Grief counselling to work through feelings of loss, fear, or shame",
                "Permission to grieve the version of life you imagined but no longer have"
            ]
        },
        "familyGrief": {
            "title": "Grieving the Loss of Family Life & Children's Stability (Family Grief)",
            "description": "Your heart breaks most over the family you once had, or the family you hoped to give your children. Co-parenting, custody arrangements, and time apart can intensify this grief. You may carry guilt, even if you made the best decision you could.",
            "why": "You may have imagined growing old with your spouse and watching your kids grow up in one home. Divorce shatters that vision. You're not only navigating your own pain but also witnessing your children's struggles, which can intensify guilt and heartbreak. Your grief is rooted in love for your family, hopes for your kids, and a desire for togetherness that now feels fractured.",
            "recommendations": [
                "Peer support from other divorced parents",
                "Child-focused resources to help your kids adjust",
                "Grief counselling for yourself (and possibly your children) to process loss and rebuild connection"
            ]
        },
        "existentialGrief": {
            "title": "Grieving the Loss of Identity, Self, and Future Vision (Existential Grief)",
            "description": "You're not just grieving a person or a house, you're grieving a version of yourself. Divorce can shake your sense of identity, purpose, and direction. Even if the separation was necessary, the emotional fallout can feel like a loss of self.",
            "why": "Your marriage may have shaped your identity: partner, co-parent, provider, caregiver. Without those roles, you might feel uncertain or disconnected from who you are. Some people lose sight of themselves in the relationship, and the grief that follows is not just about the marriage ending, it's about mourning the version of yourself you let go of, or lost entirely.",
            "recommendations": [
                "Journaling or creative expression to explore your identity",
                "Grief counselling to reflect on who you were and who you're becoming",
                "Compassionate space to rediscover your values, voice, and direction"
            ]
        }
    }
    
    # Find dominant grief type
    max_score = max(scores.values())
    dominant_types = [grief_type for grief_type, score in scores.items() if score == max_score]
    
    # Check for significant secondary types (within 18% of max score)
    threshold = max_score * 0.82
    significant_types = [grief_type for grief_type, score in scores.items() if score >= threshold]
    
    return {
        "scores": scores,
        "dominant_grief": dominant_types[0] if dominant_types else "spousalGrief",
        "significant_types": significant_types,
        "interpretations": grief_types
    }



def display_admin_panel():
    """Display admin panel with user statistics"""
    st.title("🔐 Admin Dashboard - Divorce Grief Quiz")
    
    all_responses = load_all_responses()
    
    if not all_responses:
        st.info("No user responses recorded yet.")
        return
    
    # Summary statistics
    st.subheader("📊 Usage Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(all_responses))
    
    with col2:
        completed_users = sum(1 for data in all_responses.values() if data.get('completed', False))
        st.metric("Completed Quizzes", completed_users)
    
    with col3:
        if all_responses:
            latest_timestamp = max(data['timestamp'] for data in all_responses.values())
            latest_date = datetime.fromisoformat(latest_timestamp).strftime('%Y-%m-%d')
            st.metric("Latest Response", latest_date)
    
    with col4:
        emails_provided = sum(1 for data in all_responses.values() if data.get('email', '').strip())
        st.metric("Emails Provided", emails_provided)
    
    # Grief type distribution
    st.subheader("📈 Grief Type Distribution")
    grief_counts = {"spousalGrief": 0, "materialGrief": 0, "familyGrief": 0, "existentialGrief": 0}
    
    for data in all_responses.values():
        if 'scores' in data:
            scores = data['scores']
            max_score = max(scores.values())
            dominant_types = [grief_type for grief_type, score in scores.items() if score == max_score]
            if dominant_types:
                grief_counts[dominant_types[0]] += 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Spousal Grief", grief_counts["spousalGrief"])
    with col2:
        st.metric("Material Grief", grief_counts["materialGrief"])
    with col3:
        st.metric("Family Grief", grief_counts["familyGrief"])
    with col4:
        st.metric("Existential Grief", grief_counts["existentialGrief"])
    
    # User list
    st.subheader("👥 User Responses")
    
    for user_id, data in sorted(all_responses.items(), key=lambda x: x[1]['timestamp'], reverse=True):
        email = data.get('email', 'No email provided')
        scores = data.get('scores', {})
        
        with st.expander(f"User: {user_id} - {data['timestamp'][:10]} - {email}"):
            st.write(f"**Email:** {email}")
            
            if scores:
                st.write("**Grief Scores:**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"Spousal: {scores.get('spousalGrief', 0)}")
                with col2:
                    st.write(f"Material: {scores.get('materialGrief', 0)}")
                with col3:
                    st.write(f"Family: {scores.get('familyGrief', 0)}")
                with col4:
                    st.write(f"Existential: {scores.get('existentialGrief', 0)}")
            
            st.write("---")
            st.write("**Responses:**")
            
            responses = data['responses']
            for question in QUESTIONS:
                response_key = responses.get(question['id'])
                if response_key:
                    for option_key, option_text in question['options']:
                        if option_key == response_key:
                            st.write(f"**{question['question']}**")
                            st.write(f"*{option_text}*")
                            st.write("")
                            break
    
    # Export option
    st.subheader("📥 Export Data")
    if st.button("Download All Responses as JSON"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(all_responses, indent=2),
            file_name=f"grief_quiz_responses_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def display_question(question_idx):
    """Display a single question with radio button options"""
    question = QUESTIONS[question_idx]
    
    st.subheader(f"Question {question_idx + 1} of {len(QUESTIONS)}")
    st.write(f"**{question['question']}**")
    
    # Create radio button options
    options = [option[1] for option in question['options']]
    option_keys = [option[0] for option in question['options']]
    
    # Get previous response if it exists
    previous_response = st.session_state.responses.get(question['id'])
    previous_index = None
    if previous_response:
        try:
            previous_index = option_keys.index(previous_response)
        except ValueError:
            previous_index = None
    
    selected = st.radio(
        "Select your response:",
        options,
        index=previous_index,
        key=f"q_{question_idx}"
    )
    
    # Store the response
    if selected:
        selected_index = options.index(selected)
        st.session_state.responses[question['id']] = option_keys[selected_index]
    
    return selected is not None

def display_results():
    """Display the personalized grief assessment results"""
    st.header("💔 Your Divorce Grief Assessment Results")
    
    # Calculate scores and interpretation
    scores = calculate_grief_scores(st.session_state.responses)
    interpretation = get_grief_interpretation(scores)
    
    # Important note
    st.info("**Important note about your results:** It's common to experience more than one kind of grief after a separation or divorce. You might find that two, three, or even all four of these grief types resonate with you. That's because loss in divorce is rarely one-dimensional, it can affect your relationship, finances, family life, and sense of self all at once. Recognizing the different layers of your grief can help you make sense of what you're feeling and begin to heal each part.")
    
    # Display primary grief type(s)
    st.subheader("🎯 Your Primary Grief Pattern")
    
    primary_type = interpretation['dominant_grief']
    primary_info = interpretation['interpretations'][primary_type]
    
    st.write(f"**{primary_info['title']}**")
    st.write(primary_info['description'])
    
    st.write("**Why you might be experiencing this:**")
    st.write(primary_info['why'])
    
    st.write("**What might help:**")
    for rec in primary_info['recommendations']:
        st.write(f"• {rec}")
    
    # Show secondary types if significant
    if len(interpretation['significant_types']) > 1:
        st.subheader("🔄 Additional Grief Patterns")
        st.write("Based on your responses, you're also experiencing significant grief in these areas:")
        
        for grief_type in interpretation['significant_types']:
            if grief_type != primary_type:
                info = interpretation['interpretations'][grief_type]
                with st.expander(f"📍 {info['title']}"):
                    st.write(info['description'])
                    st.write("**What might help:**")
                    for rec in info['recommendations']:
                        st.write(f"• {rec}")
    
    # Display scores
    st.subheader("📊 Your Grief Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        percentage = round((scores['spousalGrief'] / 13) * 100)
        st.metric("Spousal Grief", f"{scores['spousalGrief']}/13", f"{percentage}%")
    
    with col2:
        percentage = round((scores['materialGrief'] / 13) * 100)
        st.metric("Material Grief", f"{scores['materialGrief']}/13", f"{percentage}%")
    
    with col3:
        percentage = round((scores['familyGrief'] / 13) * 100)
        st.metric("Family Grief", f"{scores['familyGrief']}/13", f"{percentage}%")
    
    with col4:
        percentage = round((scores['existentialGrief'] / 13) * 100)
        st.metric("Existential Grief", f"{scores['existentialGrief']}/13", f"{percentage}%")
    
    st.write("*Many people experience more than one type of grief, there's no \"right\" answer, only insight. Your healing journey is unique to you.*")
    
    # Additional resources
    st.subheader("📚 Support & Resources")
    st.write("Consider these resources as you navigate your healing journey:")
    st.write("• **Divorce Coaching:** Contact Karen at The Divorce Workshop (karen@divorceworkshop.ca) for personalized support")
    st.write("• Local divorce support groups in your community")
    st.write("• Grief counselling or therapy focused on divorce and life transitions")
    st.write("• Online resources for specific grief types")
    st.write("• Mindfulness and self-care practices for emotional regulation")
    
    # Results saved automatically for admin review

# Main app logic
def main():
    # Force clear any admin session state for public users
    query_params = st.query_params
    
    # Check for admin URL parameter  
    if query_params.get("admin") == "karen2025":
        display_admin_panel()
        return
    
    # Clear any admin session state if not admin
    if 'admin_mode' in st.session_state:
        del st.session_state.admin_mode
    
    st.title("💔 What Are You Really Grieving in Your Divorce?")
    st.write("*A compassionate assessment to help you understand and navigate your unique grief journey*")
    
    if not st.session_state.show_results:
        # Questionnaire phase
        if st.session_state.current_step < len(QUESTIONS):
            # Progress bar
            progress = (st.session_state.current_step + 1) / len(QUESTIONS)
            st.progress(progress)
            
            # Display current question
            question_answered = display_question(st.session_state.current_step)
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.session_state.current_step > 0:
                    if st.button("← Previous"):
                        st.session_state.current_step -= 1
                        st.rerun()
            
            with col3:
                if question_answered:
                    if st.session_state.current_step < len(QUESTIONS) - 1:
                        if st.button("Next →"):
                            st.session_state.current_step += 1
                            st.rerun()
                    else:
                        # Email collection before final submission
                        st.write("---")
                        st.subheader("📧 Get Your Results")
                        st.write("Your results will be displayed here and optionally sent to your email.")
                        email = st.text_input("Enter your email address (optional):", 
                                            value=st.session_state.user_email,
                                            placeholder="your.email@example.com")
                        
                        if email != st.session_state.user_email:
                            st.session_state.user_email = email
                        
                        if st.button("Get My Grief Assessment →"):
                            # Save user response before showing results
                            save_user_response(st.session_state.user_id, st.session_state.responses, st.session_state.user_email or "")
                            st.session_state.show_results = True
                            st.rerun()
        
        # Show review section if all questions answered
        if len(st.session_state.responses) == len(QUESTIONS):
            st.write("---")
            st.subheader("Review Your Responses")
            
            for question in QUESTIONS:
                response_key = st.session_state.responses.get(question['id'])
                if response_key:
                    for option_key, option_text in question['options']:
                        if option_key == response_key:
                            st.write(f"**{question['question']}**")
                            st.write(f"*{option_text}*")
                            st.write("")
                            break
    
    else:
        # Results phase
        display_results()
        
        # Option to retake questionnaire
        st.write("---")
        if st.button("🔄 Take Assessment Again"):
            st.session_state.current_step = 0
            st.session_state.responses = {}
            st.session_state.show_results = False
            st.session_state.user_email = ""
            st.rerun()

if __name__ == "__main__":
    main()
