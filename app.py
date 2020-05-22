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
import pandas as pd
import numpy as np

import hypergraphs as hg

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

st.markdown('See the full documentation [here](http://graphbrain.net/reference/notation.html)')

text = st.text_area("Text to analyze", DEFAULT_TEXT)
sent = parser.parse(text)['parses'][0]

sent = [s for s in sent['main_edge'].subedges() if s.is_atom() == False]


html = ''
for edge in sent:
    
    html += '<p>'
    html += notebook._edge2html(edge, roots_only=False, formatting='oneline')
    html += '</p>'

st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)

sentences = []
for edge in sent:
    if edge is not None:
        edge_verbs = []
        for edge_verb in hg.split(edge):
            edge_verbs.extend(hg.edge_split(edge_verb))
        sentences.append(edge_verbs)

sentences = pd.concat([pd.DataFrame(s) for s in sentences])
sentences = sentences.drop_duplicates()
sentences = sentences[['predicate','arg','entity','eID']].dropna()

sentences['predRole1'] = sentences.apply(lambda x: x['predicate'].role()[0], axis = 1)
sentences['predRole2'] = sentences.apply(lambda x: x['predicate'].role()[-1], axis = 1)
sentences['predicate'] = sentences.apply(lambda x: x['predicate'].label(), axis = 1)

df = []
for _,row in sentences.iterrows():
    for he in hg.extract_taxonomy(row['entity'], edge_id = row['eID'], verb = row['predicate'], trigger = row['arg'], single_concept = True):
        df.append([he['tax_id'],he['verb'],row['predRole1'],row['predRole2'],he['builder'],he['trigger'],he['main'],he['aux']])
        
df = pd.DataFrame(df,columns = ['edgeId','verb','predRol1','predRole2','builder','trigger','main','aux'])

#df = pd.DataFrame(df,columns = ['edgeId','verb','predRol1','predRole2','builder','trigger','main','aux'])
df['role'] = df['trigger'].apply(lambda x: x if type(x) is str else 'x')
df['trigger'] = df['trigger'].apply(lambda x: np.nan if type(x) is str else x.label())
df['main_type'] = df['main'].apply(lambda x: x.type() if not pd.isnull(x) else x)
df['main'] = df['main'].apply(lambda x: x.label() if not pd.isnull(x) else x)
df['aux_type'] = df['aux'].apply(lambda x: x.type() if not pd.isnull(x) else x)
df['aux'] = df['aux'].apply(lambda x: x.label() if not pd.isnull(x) else x)
df = df.drop('edgeId', axis = 1).drop_duplicates()


st.table(df.fillna('-'))


csv = df.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
href = f'<a href="data:file/csv;base64,{b64}" download="hyperedges.csv">Download hyperedges</a>'
st.sidebar.markdown(href, unsafe_allow_html=True)
