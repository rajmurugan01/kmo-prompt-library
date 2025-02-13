import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set the custom CSS for Streamlit
def set_custom_css():
    st.markdown("""
    <style>
    /* Change the background color of the entire page */
    body {
        background-color: #00008B;  /* Dark purple color */
        color: white;  /* Change text color to white for better contrast */
    }

    /* Style for the main content area */
    .stApp {
        background-color: #000044;  /* Dark purple color */
    }
                
    /* Style for the main select box */
    div[data-baseweb="select"] > div {
        background-color: #734d26 !important;
        color: white !important;
    }

    ul[data-baseweb="menu"] li {
        color: white !important;
    }

    ul[data-baseweb="menu"] li:hover {
        background-color: #734d26 !important;
    }

    /* Style for the selected option */
    div[data-baseweb="select"] > div > div {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to load data from CSV
def load_data():
    if not os.path.exists('prompt_elements.csv'):
        df = pd.DataFrame(columns=['title', 'type', 'content'])
        df.to_csv('prompt_elements.csv', index=False)
    return pd.read_csv('prompt_elements.csv')

# Function to save data to CSV
def save_data(df):
    df.to_csv('prompt_elements.csv', index=False)

# Function to save prompt to CSV
def save_prompt(name, prompt):
    if not os.path.exists('prompt_history.csv'):
        df = pd.DataFrame(columns=['name', 'timestamp', 'prompt'])
        df.to_csv('prompt_history.csv', index=False)
    else:
        df = pd.read_csv('prompt_history.csv')
    
    new_row = pd.DataFrame({'name': [name], 'timestamp': [datetime.now()], 'prompt': [prompt]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('prompt_history.csv', index=False)

# Function to create a new element
def create_element():
    st.header("Create New Element")
    
    element_type = st.selectbox("Select Element Type", 
                                ['role', 'goal', 'audience', 'context', 'output', 'tone'])
    title = st.text_input("Enter Element Title")
    content = st.text_area("Enter Element Content")
    
    if st.button("Add Element"):
        df = load_data()
        new_row = pd.DataFrame({'title': [title], 'type': [element_type], 'content': [content]})
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("Element added successfully!")

def create_element():
    with st.expander("Create New Element", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            element_type = st.selectbox("Type", ['role', 'goal', 'audience', 'context', 'output', 'tone'], key="new_type")
            title = st.text_input("Title", key="new_title")
        with col2:
            content = st.text_area("Content", key="new_content", height=100)
        if st.button("Add Element", key="add_element"):
            df = load_data()
            new_row = pd.DataFrame({'title': [title], 'type': [element_type], 'content': [content]})
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Element added successfully!")

def build_prompt():
    df = load_data()
    
    def create_section(section_title, element_type, multi_select=False):
        elements = df[df['type'] == element_type]
        options = ["Skip", "Write your own"] + elements['title'].tolist()
        
        if multi_select:
            selected_option = st.multiselect(section_title, options, key=f"select_{element_type}")
        else:
            selected_option = st.selectbox(section_title, options, key=f"select_{element_type}")
        
        custom_content = ""
        if "Write your own" in selected_option:
            custom_content = st.text_input(f"Custom {section_title}", key=f"custom_{element_type}")
        
        return selected_option, custom_content

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_role, custom_role = create_section("Role", 'role')
        selected_goal, custom_goal = create_section("Goal", 'goal')
    with col2:
        selected_audiences, custom_audience = create_section("Target Audience", 'audience', multi_select=True)
        selected_contexts, custom_context = create_section("Context", 'context', multi_select=True)
    with col3:
        selected_outputs, custom_output = create_section("Output", 'output', multi_select=True)
        selected_tone, custom_tone = create_section("Tone", 'tone')
        recursive_feedback = st.checkbox("Request recursive feedback")

    # Generate prompt
    prompt = ""
    if selected_role != "Skip":
        prompt += f"Role: {custom_role if selected_role == 'Write your own' else df[df['title'] == selected_role]['content'].values[0]}\n\n"
    if selected_goal != "Skip":
        prompt += f"Goal: {custom_goal if selected_goal == 'Write your own' else df[df['title'] == selected_goal]['content'].values[0]}\n\n"
    if selected_audiences != ["Skip"]:
        prompt += "Target Audience:\n" + (custom_audience if "Write your own" in selected_audiences else "\n".join([df[df['title'] == a]['content'].values[0] for a in selected_audiences if a != "Skip"])) + "\n\n"
    if selected_contexts != ["Skip"]:
        prompt += "Context:\n" + (custom_context if "Write your own" in selected_contexts else "\n".join([df[df['title'] == c]['content'].values[0] for c in selected_contexts if c != "Skip"])) + "\n\n"
    if selected_outputs != ["Skip"]:
        prompt += "Output:\n" + (custom_output if "Write your own" in selected_outputs else "\n".join([df[df['title'] == o]['content'].values[0] for o in selected_outputs if o != "Skip"])) + "\n\n"
    if selected_tone != "Skip":
        prompt += f"Tone: {custom_tone if selected_tone == 'Write your own' else df[df['title'] == selected_tone]['content'].values[0]}"
    
    if recursive_feedback:
        prompt += "\n\nBefore you provide the response, please ask me any questions that you feel could help you craft a better response. If you feel you have enough information to craft this response, please just provide it."

    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_area("Generated Prompt", value=prompt, height=250, key="generated_prompt")
    with col2:
        if st.button("Copy to Clipboard"):
            st.write("Prompt copied to clipboard!")
            st.code(prompt)  # This will display the prompt as a code block
            st.markdown(f"<textarea style='position:absolute;left:-9999px'>{prompt}</textarea>", unsafe_allow_html=True)
            st.markdown(
                "<script>navigator.clipboard.writeText(document.querySelector('textarea').value);</script>",
                unsafe_allow_html=True
            )
    col1, col2 = st.columns(2)
    with col1:
        prompt_name = st.text_input("Prompt Name")
    with col2:
        if st.button("Save Prompt"):
            if prompt_name:
                save_prompt(prompt_name, prompt)
                st.success("Prompt saved successfully!")

def edit_elements():
    df = load_data()
    
    if df.empty:
        st.warning("No elements found. Please create some elements first.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        all_types = ['All'] + sorted(df['type'].unique().tolist())
        selected_type = st.selectbox("Filter by Type", all_types, key="filter_type")
    
    filtered_df = df if selected_type == 'All' else df[df['type'] == selected_type]
    
    if filtered_df.empty:
        st.warning(f"No elements found for type: {selected_type}")
        return
    
    for index, row in filtered_df.iterrows():
        with st.expander(f"{row['title']} ({row['type']})", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("Title", value=row['title'], key=f"title_{index}")
                new_type = st.selectbox("Type", ['role', 'goal', 'audience', 'context', 'output', 'tone'],
                                        index=['role', 'goal', 'audience', 'context', 'output', 'tone'].index(row['type']),
                                        key=f"type_{index}")
            with col2:
                new_content = st.text_area("Content", value=row['content'], key=f"content_{index}", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{index}"):
                    df.at[index, 'title'] = new_title
                    df.at[index, 'type'] = new_type
                    df.at[index, 'content'] = new_content
                    save_data(df)
                    st.success("Updated successfully!")
                    st.experimental_rerun()
            with col2:
                if st.button("Delete", key=f"delete_{index}"):
                    df = df.drop(index)
                    save_data(df)
                    st.success("Deleted successfully!")
                    st.experimental_rerun()

def browse_prompts():
    if not os.path.exists('prompt_history.csv'):
        st.warning("No prompts found. Please create and save some prompts first.")
        return
    
    df = pd.read_csv('prompt_history.csv')
    
    for index, row in df.iterrows():
        with st.expander(f"{row['name']} - {row['timestamp']}", expanded=False):
            st.text_area("Prompt Content", value=row['prompt'], height=150, key=f"prompt_{index}")

def main():
    st.set_page_config(layout="wide")
    set_custom_css()
    st.title("KMo's Prompt Creation Tool!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Element Creator", "Element Editor", "Prompt Builder", "Browse Prompts"])
    
    with tab1:
        create_element()
    with tab2:
        edit_elements()
    with tab3:
        build_prompt()
    with tab4:
        browse_prompts()

if __name__ == "__main__":
    main()
