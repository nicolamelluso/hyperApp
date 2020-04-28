# coding: utf-8
"""
Example of a Streamlit app for an interactive spaCy model visualizer. You can
either download the script, or point streamlit run to the raw URL of this
file. For more details, see https://streamlit.io.
Installation:
pip install streamlit
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download de_core_news_sm
Usage:
streamlit run streamlit_spacy.py
"""
from __future__ import unicode_literals

import streamlit as st
import base64
import os

from graphbrain.parsers import *
from graphbrain import notebook

@st.cache(allow_output_mutation=True)
def load_parser():
    return create_parser(name='en')

parser = load_parser()
#from graphbrain import *


DEFAULT_TEXT = "Mark Zuckerberg is the CEO of Facebook."
HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 0.5rem; margin-bottom: 0.5rem">{}</div>"""



st.header("Graphbrain")

text = st.text_area("Text to analyze", DEFAULT_TEXT)
sent = parser.parse(text)[0]
sent = [s for s in sent['main_edge'].subedges() if s.is_atom() == False]


html = ''
for edge in sent:
    
    html += '<p>'
    html += notebook._edge2html(edge, roots_only=False, formatting='oneline')
    html += '</p>'

st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)