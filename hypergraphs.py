#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import copy

from graphbrain.parsers import *
from graphbrain.notebook import *
#parser = create_parser(name='en')

from tqdm.notebook import tqdm


# edge = hedge('((further/a/en was/pd.xscr.<f-----/en) (and/pm/en ((to/ai/en build/pd.o.-i-----/en) (+/b.am/. ergonomics/cc.p/en awareness/cc.s/en)) (develop/p!.o.-i-----/en (a/md/en (continuous/ma/en (in/br.ma/en (+/b.am/. learning/cc.s/en process/cc.s/en) (the/md/en company/cc.s/en)))))) it/ci/en necessary/ca/en ((to/ai/en use/pc.ox.-i-----/en) (more/mc/en (+/b.am/. ergonomics/cc.p/en tools/cc.p/en)) (through/t/en (in/br.ma/en (’/bp.am/en workers/cc.p/en participation/cc.s/en) (different/ma/en workplaces/cc.p/en)))))')

# edge = hedge('((was/av.<f-----/en introduced/pd.rpx.<pf----/en) (took/pr.xso.<f-----/en (after/t/en (a/md/en week/cc.s/en)) (a/md/en (one/m#/en (+/b.am/. day/cc.s/en workshop/cc.s/en))) place/cc.s/en) (:/b/. (an/md/en (+/b.am/. ergonomics/cc.s/en checklist/cc.s/en)) 2/c#/en) (in/t/en (of/br.ma/en one/c#/en (:/b/. (the/md/en divisions/cc.p/en) (and/b+/en (the/md/en (+/b.am machinery/cm/en division/cc.s/en)) (+/b.am equipment/cc.s/en division/cc.s/en))))))')

# edge = hedge('(and/pm/en ((were/av.<f-----/en discussed/pd.px.<pf----/en) (and/b+/en (+/b.am (the/md/en (+/b.mm/. (+/b.am/. sc/cp.s/en ’s/cm/en) ’/c/en)) responsibilities/cc.p/en) (+/b.am ags/cc.p/en responsibilities/cc.p/en)) (with/t/en (the/md/en group/cc.s/en))) ((were/av.<f-----/en suggested/pd.pr.<pf----/en) (the/md/en following/c/en) (setting/pc.o?.|pg----/en (and/b+/en policies/cc.p/en (for/br.ma/en (administrative/ma/en procedures/cc.p/en) (their/mp/en activities/cc.p/en))) (and/pm/en (interacting/pd.x.|pg----/en (with/t/en ags/cc.p/en)) (documenting/pd.o?.|pg----/en (the/md/en (of/br.ma/en progress/cc.s/en (the/md/en project/cc.s/en))) (promoting/pd.o?.|pg----/en (+/b.am/. ag/cp.s/en activities/cc.p/en) (and/pm/en reviewing/pd..|pg----/en (approving/pd.o.|pg----/en (for/br.ma/en (+/b.aam/. ags/cp.s/en ’/c/en plans/cc.p/en) (+/b.am/. ergonomics/cc.s/en implementation/cc.s/en))) (and/pm/en supporting/pd..|pg----/en (confirming/pd.o.|pg----/en (:/b/. (+/b.aam/. ag/cp.s/en activity/cc.s/en plans/cc.p/en) (+/b.mm/. time/cc.s/en (and/b+/en place/cc.s/en budget/cc.s/en))))))))))) (and/pm/en (evaluating/pd.ox.|pg----/en (+/b.aam/. ags/cp.s/en ’/c/en activities/cc.p/en) (on/t/en (a/md/en (regular/ma/en basis/cc.s/en)))) (designing/pd.o.|pg----/en (and/b+/en rewards/cc.p/en (of/br.ma/en systems/cc.p/en (for/br.ma/en motivation/cc.s/en ags/cc.p/en))))))')
# text = 'machine learning process'
# edge = parser.parse(text)['parses'][0]['main_edge']


def strip_concept(edge):
    
    
    if edge.is_atom():
        return edge
    
    if edge[0].type() in ['md','m#','mp','ms','mr','w']:
        return strip_concept(edge[1])
    
    else:
        return edge


# # REF

def extract_taxonomy(edge, edge_id = 'E0001', single_concept = False, verb = None, trigger = None):
    
    edge_depths = set([e.depth() for e in edge.subedges()]) - {0}

    taxonomy = []
    

            
        
    for depth in edge_depths:
        taxonomy.extend(extract_taxonomy_(edge,edge_id = edge_id, depth = depth, taxonomy_ = taxonomy, verb = verb, trigger = trigger))
        
    if single_concept == True:
        if taxonomy == []:
            
            tax = {}
            tax['edge'] = edge
            tax['tax_id'] = edge_id
            tax['main'] = edge
            tax['builder'] = np.nan
            tax['aux'] = np.nan
            tax['depth'] = 0
            tax['main_dep'] = np.nan
            tax['aux_dep'] = np.nan
            
            if verb is not None:
                tax['verb'] = verb
                tax['trigger'] = trigger
                
            taxonomy.append(tax)
        
    return taxonomy


def extract_taxonomy_(edge, edge_id = 'E0001', depth = 1, taxonomy_ = None, verb = None, trigger = None):
    
    
        
    if taxonomy_ is not None:
        taxonomy_ = pd.DataFrame(taxonomy_)
        
    taxonomy = []
    
    for id,he in enumerate(edge.subedges()):
        if he.is_atom():
            continue
            
        if he.depth() != depth:
            continue
            
        if set(he[0].argroles()) == {'a','m'}:
            
            tax = {}
            main = he.edges_with_argrole('m')[0]
            
            tax['edge'] = he
            tax['tax_id'] = edge_id + 'T' + str(id)
            tax['main'] = main
            tax['builder'] = he[0].label()
            tax['depth'] = he.depth()
            tax['main_dep'] = np.nan
            tax['aux_dep'] = np.nan
            
            aux = he.edges_with_argrole('a')[0]

            for a in he.edges_with_argrole('a'):
                if a != aux:
                    aux = aux.nest(a)
                    
            tax['aux'] = aux
            
            if depth > 1:
                if (taxonomy_ is not None) & (not taxonomy_.empty):
                    
                    df = taxonomy_[taxonomy_['edge'] == strip_concept(main)]
                    
                    if not df.empty:
                        tax['main_dep'] = ';'.join(df['tax_id'].values)
                
                    df = taxonomy_[taxonomy_['edge'] == strip_concept(aux)]
                    if not df.empty:
                        tax['aux_dep'] = ';'.join(df['tax_id'].values)
            
            if verb is not None:
                tax['verb'] = verb
                tax['trigger'] = trigger
            
            
            taxonomy.append(tax)
                
    return taxonomy


# ### Test



# # Ergonomics

# ## VerbSplit

def split(edge, edge_dep = 'E0001'):
    
    output = []
    
    edge_list = [he for he in edge.subedges() if 'r' in he.type()]
    
    for edge in edge_list:
        output.extend(verb_split(edge, edge_dep = edge_dep))
    
    return output    

def verb_split(edge, edge_dep = 'E0001', plain = False):
    
                
    output = []
    buffer = []
    
    if not edge.is_atom():
        if (edge[0].type() == 'pm') | (edge[0].to_str() == ':/b/.'):
            
            for id in range(1,len(edge)):
                
                buffer.append((edge_dep + 'E{0:03d}'.format(id),edge[id]))
                buffer.append((edge_dep + 'E{0:03d}'.format(id),edge[id]))

    if type(edge[0]) == str:
        for edge_verb in buffer:
            output.extend(edge_split(edge_verb))
            
        return output
    
            
    for arg in edge[0].argroles():
        for id,he in enumerate(edge.edges_with_argrole(arg)):
            
            out = {}            

            if not he.is_atom():
                if (he[0].type() == 'pm') | (he[0].to_str() == ':/b/.'):
                    for he_id in range(1,len(he)):
                        buffer.append((edge_dep + 'E{0:03d}'.format(he_id),he[he_id]))
                        buffer.append((edge_dep + 'E{0:03d}'.format(he_id),he[he_id]))
                    continue
                elif 'p' in he[0].type():
                    buffer.append((edge_dep + 'E{0:03d}'.format(id),he))
                    continue
            
            out['verb'] = edge[0]
            out['predicate'] = edge[0].predicate()
            out['arg'] = arg
            out['entity'] = he
            out['eID'] = edge_dep + 'E{0:03d}'.format(id)
            
            if plain == True:
                out[arg] = he
            
            output.append(out)
            
    for id,he in buffer:
        output.extend(verb_split(edge = he, edge_dep = id, plain = plain))
#        print(he)
    return output


# ## Edge_Split

def stopper(edge):
    if set([he.is_atom() for he in edge]) == {True}:
        return True
    else:
        return False

def edge_split(edge_verb):
    
    buffer = []
    output = []
    
    edge = edge_verb['entity']
        

    if edge.is_atom():
        output.append(edge_verb)
            
    elif edge[0].type() in ['md','m#','mp','ms','mr','w','mc']:
        edge_verb['entity'] = edge[1]
        buffer.append(edge_verb)
        
    elif stopper(edge):
        output.append(edge_verb)

    
    elif edge[0].type() in ['ma']:
        #buffer.append(edge_verb)
        if not stopper(edge):
            edge_verb['entity'] = edge[1]
            buffer.append(edge_verb)
        else:
            output.append(edge_verb)
        
    elif (edge[0].to_str() == ':/b/.') | (edge[0].to_str() == 'and/b+/en') | (edge[0].to_str() == 'and/m+/en') | (edge[0].to_str() == '&/b+/en') | (edge[0].to_str() == 'or/b+/en'):
        for e in edge[1:]:

            edge_verb['entity'] = e
            buffer.append(copy.deepcopy(edge_verb))
            
    elif (edge[0].label() == '+'):
        if not stopper(edge):
            for e in edge[1:]:
                edge_verb['entity'] = e
                buffer.append(copy.deepcopy(edge_verb))
            
    elif edge[0].label() == 'of':
        if edge.depth() < 10:
            output.append(edge_verb)
        
        
    elif (edge[0].type() in ['br']):# & (edge[0].label() != 'of'):
        for e in edge.edges_with_argrole('m'):
            edge_verb['entity'] = e
            buffer.append(copy.deepcopy(edge_verb))
        for e in edge.edges_with_argrole('a'):
            
            if edge[0].label() not in ['like']:
                edge_verb['arg'] = edge[0]
            else:
                pass
            edge_verb['entity'] = e
            buffer.append(copy.deepcopy(edge_verb))
            
    elif edge[0].type() in ['t','x']:
        edge_verb['entity'] = edge[1]
        edge_verb['arg'] = edge[0]
        buffer.append(copy.deepcopy(edge_verb))
            
    else:
        output.append(edge_verb)
#        if stopper(edge):
#            output.append(edge_verb)
#        else:
#            buffer.append(edge_verb)

    for edge_verb in buffer:

        output.extend(edge_split(edge_verb))
    
    return output


# ### Test `edge_split` 

# ## Problemi
# - muore sugli `of`
# - si blocca quando trova i predicate senza `argrole`
