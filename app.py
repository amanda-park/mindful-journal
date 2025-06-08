import streamlit as st
import random
import ollama
from datetime import datetime
from prompts import JOURNALING_PROMPTS
from llm_analyzer import LLMAnalyzer

# Initialize session state
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = None
if 'journal_entry' not in st.session_state:
    st.session_state.journal_entry = ""
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'llm_analyzer' not in st.session_state:
    try:
        st.session_state.llm_analyzer = LLMAnalyzer()
        st.session_state.ollama_available = True
    except Exception as e:
        st.session_state.llm_analyzer = None
        st.session_state.ollama_available = False
        st.session_state.ollama_error = str(e)

def get_new_prompt():
    """Get a random journaling prompt"""
    return random.choice(JOURNALING_PROMPTS)

def reset_session():
    """Reset the journaling session"""
    st.session_state.current_prompt = None
    st.session_state.journal_entry = ""
    st.session_state.analysis_complete = False
    st.session_state.conversation_history = []

def generate_export_content(include_summary=False):
    """Generate content for export"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"Journal Session Export\n"
    content += f"Date: {timestamp}\n"
    content += "=" * 50 + "\n\n"
    
    # Add the prompt
    content += f"Journaling Prompt:\n{st.session_state.current_prompt}\n\n"
    
    # Add the journal entry
    content += f"Your Reflection:\n{st.session_state.journal_entry}\n\n"
    
    if st.session_state.conversation_history:
        content += "Session Analysis & Conversation:\n"
        content += "-" * 30 + "\n\n"
        
        for message in st.session_state.conversation_history:
            if message['type'] == 'analysis':
                content += "AI Analysis:\n"
                content += message['content'] + "\n\n"
            elif message['type'] == 'user_question':
                content += "Your Question:\n"
                content += message['content'] + "\n\n"
            elif message['type'] == 'ai_response':
                content += "AI Response:\n"
                content += message['content'] + "\n\n"
    
    # Add summary if requested and AI is available
    if include_summary and st.session_state.ollama_available and st.session_state.llm_analyzer is not None:
        try:
            summary_prompt = f"""Please provide a concise summary of this journaling session focusing on:
1. Key emotions and themes
2. Main insights discovered
3. Progress or growth identified
4. Important action items or reflections to remember

Session content:
Prompt: {st.session_state.current_prompt}
Entry: {st.session_state.journal_entry}
"""
            
            analyzer = st.session_state.llm_analyzer
            summary_response = analyzer.continue_conversation(
                [{'type': 'user_entry', 'content': summary_prompt}], 
                "Please provide the summary as requested."
            )
            
            content += "\n" + "=" * 50 + "\n"
            content += "SESSION SUMMARY\n"
            content += "=" * 50 + "\n\n"
            content += summary_response + "\n"
            
        except Exception:
            content += "\n(Summary generation failed - exported full conversation instead)\n"
    
    return content

def create_filename():
    """Create a filename for the export"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"journal_session_{timestamp}.txt"

# Main app
st.title("🌱 Dynamic Journaling Tool")
st.write("A supportive space for reflection and growth through mindful journaling.")

# Show Ollama status
if not st.session_state.ollama_available:
    st.error("🔌 Local LLM (Ollama) not available. You can still use the journaling prompts, but analysis features require Ollama to be installed and running.")
    with st.expander("How to set up Ollama"):
        st.write("""
        1. Install Ollama from https://ollama.com/download
        2. Run: `ollama pull llama2` (or another model)
        3. Start Ollama service
        4. Refresh this page
        """)

# Sidebar for session controls
with st.sidebar:
    st.header("Session Controls")
    if st.button("New Journal Entry", type="primary"):
        reset_session()
        st.rerun()
    
    if st.button("Get New Prompt"):
        st.session_state.current_prompt = get_new_prompt()
        st.session_state.journal_entry = ""
        st.session_state.analysis_complete = False
        st.rerun()
    # models = [model.model for model in ollama.list()["models"]] 
    # st.session_state["model"] = st.selectbox("Choose your model", models)
        # Model selection
    if st.session_state.ollama_available and st.session_state.llm_analyzer is not None:
        st.subheader("AI Model Settings")
        analyzer = st.session_state.llm_analyzer
        available_models = analyzer.get_available_models()
        if available_models:
            current_model = analyzer.model_name
            
            # Create display names for models
            model_display = {}
            for model in available_models:
                if "llama" in model.lower():
                    if "3.1" in model:
                        model_display[model] = f"{model} (Fast, good for conversation)"
                    elif "2" in model:
                        model_display[model] = f"{model} (Reliable, well-tested)"
                    else:
                        model_display[model] = f"{model} (Llama family)"
                elif "mistral" in model.lower():
                    model_display[model] = f"{model} (Creative, detailed responses)"
                elif "codellama" in model.lower():
                    model_display[model] = f"{model} (Code-focused)"
                else:
                    model_display[model] = model
            
            selected_model = st.selectbox(
                "Choose AI Model:",
                options=available_models,
                format_func=lambda x: model_display.get(x, x),
                index=available_models.index(current_model) if current_model in available_models else 0,
                help="Different models have varying capabilities and response styles"
            )
            
            # Show current model info
            st.caption(f"Currently using: **{current_model}**")
            
            if selected_model != current_model:
                if st.button("Switch Model", type="secondary"):
                    with st.spinner(f"Switching to {selected_model}..."):
                        try:
                            new_analyzer = LLMAnalyzer(selected_model)
                            st.session_state.llm_analyzer = new_analyzer
                            st.success(f"Switched to {selected_model}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to switch model: {str(e)}")
        else:
            st.warning("No models found in Ollama")
            st.caption("Pull a model with: `ollama pull llama3.2:1b`")
    st.divider()
    st.write("**How it works:**")
    st.write("1. Reflect on the prompt")
    st.write("2. Write your thoughts")
    if st.session_state.ollama_available:
        st.write("3. Get AI analysis & support")
        st.write("4. Continue the dialogue")
    else:
        st.write("3. Save your reflection")
        st.write("4. Set up Ollama for AI analysis")

# Get initial prompt if none exists
if st.session_state.current_prompt is None:
    st.session_state.current_prompt = get_new_prompt()

# Display current prompt
st.header("📝 Today's Prompt")
st.info(st.session_state.current_prompt)

# Journal entry section
st.header("Your Reflection")
if not st.session_state.analysis_complete:
    journal_text = st.text_area(
        "Take your time to reflect and write...",
        value=st.session_state.journal_entry,
        height=200,
        placeholder="Share your thoughts, feelings, and experiences..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Submit Entry", disabled=len(journal_text.strip()) < 10):
            if len(journal_text.strip()) >= 10:
                st.session_state.journal_entry = journal_text
                st.session_state.conversation_history.append({
                    'type': 'user_entry',
                    'content': journal_text
                })
                
                # Analyze the entry if Ollama is available
                if st.session_state.ollama_available and st.session_state.llm_analyzer is not None:
                    with st.spinner("Analyzing your entry..."):
                        try:
                            analysis = st.session_state.llm_analyzer.analyze_entry(journal_text)
                            st.session_state.conversation_history.append({
                                'type': 'analysis',
                                'content': analysis
                            })
                        except Exception as e:
                            st.error(f"Unable to analyze entry: {str(e)}")
                            st.session_state.conversation_history.append({
                                'type': 'analysis',
                                'content': "Analysis unavailable - Ollama connection failed."
                            })
                else:
                    st.session_state.conversation_history.append({
                        'type': 'analysis',
                        'content': "Your reflection has been saved. To get AI analysis and insights, please set up Ollama as described above."
                    })
                
                st.session_state.analysis_complete = True
                st.rerun()
            else:
                st.warning("Please write at least 10 characters for meaningful analysis.")

else:
    # Display the journal entry
    st.write("**Your entry:**")
    st.write(st.session_state.journal_entry)

# Display analysis and conversation
if st.session_state.analysis_complete and st.session_state.conversation_history:
    st.header("🤖 AI Analysis & Support")
    
    # Display conversation history
    for i, message in enumerate(st.session_state.conversation_history):
        if message['type'] == 'analysis':
            with st.container():
                st.markdown("**🔍 Analysis:**")
                st.markdown(message['content'])
        elif message['type'] == 'ai_response':
            with st.container():
                st.markdown("**💭 AI Response:**")
                st.markdown(message['content'])
        elif message['type'] == 'user_question':
            with st.container():
                st.markdown("**You asked:**")
                st.info(message['content'])
    
    # Continue conversation section
    if st.session_state.ollama_available:
        st.subheader("Continue the Conversation")
        st.write("Ask questions, share more thoughts, or request specific guidance:")
        
        user_question = st.text_area(
            "Your question or additional thoughts:",
            height=100,
            placeholder="How can I apply this insight? Can you help me understand this better? I'm still struggling with..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send", disabled=len(user_question.strip()) < 3):
                if len(user_question.strip()) >= 3:
                    with st.spinner("Thinking..."):
                        try:
                            analyzer = st.session_state.llm_analyzer
                            if analyzer is not None:
                                response = analyzer.continue_conversation(
                                    st.session_state.conversation_history, 
                                    user_question
                                )
                            else:
                                response = "Unable to continue conversation - Ollama not available."
                            st.session_state.conversation_history.append({
                                'type': 'user_question',
                                'content': user_question
                            })
                            st.session_state.conversation_history.append({
                                'type': 'ai_response',
                                'content': response
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Unable to continue conversation: {str(e)}")
    else:
        st.info("💡 Interactive conversation will be available once Ollama is set up and running.")

# Export functionality
if st.session_state.analysis_complete and st.session_state.journal_entry:
    st.header("📥 Export Your Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Full Export")
        st.write("Complete conversation with all AI analysis and dialogue")
        full_content = generate_export_content(include_summary=False)
        st.download_button(
            label="Download Full Session",
            data=full_content,
            file_name=create_filename(),
            mime="text/plain",
            help="Export the complete journaling session including all conversation history"
        )
    
    with col2:
        if st.session_state.ollama_available:
            st.subheader("Summary Export")
            st.write("Key insights and takeaways from your session")
            
            if st.button("Generate & Download Summary"):
                with st.spinner("Creating summary..."):
                    try:
                        summary_content = generate_export_content(include_summary=True)
                        summary_filename = create_filename().replace(".txt", "_summary.txt")
                        st.download_button(
                            label="Download Summary",
                            data=summary_content,
                            file_name=summary_filename,
                            mime="text/plain",
                            help="Export a summarized version focusing on key insights and takeaways",
                            key="summary_download"
                        )
                    except Exception as e:
                        st.error(f"Failed to generate summary: {str(e)}")
        else:
            st.subheader("Summary Export")
            st.write("Summary requires Ollama to be running")
            st.button("Generate & Download Summary", disabled=True, help="Set up Ollama to enable summary generation")

# Footer
st.divider()
st.caption("🔒 All processing happens locally on your device. Your journal entries are private and secure.")
