"""
AI Assistant page
"""
import streamlit as st


def show():
    """Show AI assistant page"""
    st.header("🤖 AI Assistant")

    st.markdown("""
    Welcome to your AI-powered assistant! I can help you with:
    - 📄 Document generation and templates
    - 📊 Data analysis and insights
    - ❓ Answering questions about your processes
    - 📝 Writing reports and summaries
    - 🔍 Finding information across modules
    """)

    # Chat interface
    st.divider()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your LIMS-QMS AI Assistant. How can I help you today?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response (mock for now)
        with st.chat_message("assistant"):
            # TODO: Integrate with Claude API
            response = f"I understand you're asking about: '{prompt}'. This is a demo response. In production, this would be powered by Claude AI to provide intelligent responses based on your organization's data."
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Quick actions sidebar
    with st.sidebar:
        st.subheader("🚀 Quick Actions")

        if st.button("📄 Generate Document"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can help you generate documents. What type of document would you like to create? (e.g., Quality Manual, Test Report, SOP)"
            })
            st.rerun()

        if st.button("📊 Analyze Data"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can analyze your data. Which module would you like me to analyze? (e.g., Projects, Quality, Financial)"
            })
            st.rerun()

        if st.button("🔍 Search Records"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can search across all your records. What are you looking for?"
            })
            st.rerun()

        if st.button("📝 Write Report"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can help you write reports. What kind of report do you need? (e.g., Monthly Summary, Audit Report, Project Status)"
            })
            st.rerun()

        st.divider()

        st.subheader("💡 Suggestions")
        st.caption("Try asking:")
        st.caption("- 'Show me all overdue tasks'")
        st.caption("- 'Generate a quality report for this month'")
        st.caption("- 'What equipment needs calibration soon?'")
        st.caption("- 'Create a new SOP template'")

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your LIMS-QMS AI Assistant. How can I help you today?"}
        ]
        st.rerun()
