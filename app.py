import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 3 Transliteration bot")

st.title('Llama3 based Transliteration Bot / 以 Llama3 為基礎的音譯機器人')

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 3 Transliteration bot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your text to transliterate!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama3 model', ['Llama3-8B-instruct-FT'], key='selected_model')
    if selected_model == 'Llama3-8B-instruct-FT':
        llm = 'meta/meta-llama-3-8b-instruct'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "What can I transliterate to Nepali language for you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "What can I transliterate to Nepali language for you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating llama3 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama3_response(prompt_input):
    string_dialogue = "You are a transliterator, expertly converting text from Romanized format (using English alphabets) to Nepali script (Devanagari). You should focus strictly on transliteration without engaging in conversations. Your transliteration skills apply to any text written in English alphabets, regardless of the underlying language. Special attention is given to correctly interpreting and transliterating common modifiers and context-sensitive words. Rules: 1) Always transliterate text directly, without requiring explicit commands. 2) Use a dataset of Romanized and pure Nepali words to enhance transliteration accuracy. 3) For words like 'vala' which can be interpreted as 'भाला' or 'वाला' and phrases such as 'tara' where context changes the meaning, ensure correct translation: - 'Mero naam tara ho' transliterates to 'मेरो नाम तारा हो' (name/star). 'Malai dudhko tara man pardaina' transliterates to 'मलाइ दुधको तर मन पर्दैन' (but). - 'Mero gharma rato tara chha' transliterates to 'मेरो घरमा रातो तार छ' (wire). 4) Notify the user if input is in any script other than Roman alphabets."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('meta/meta-llama-3-8b-instruct', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama3_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
