from flexiconc import Concordance
c = Concordance()
c.retrieve_from_clic(query=["eyes"], corpora="dickens")
c.register_wordfreq_frequency_list(p_attr="word")
n1 = c.root.add_arrangement_node(ordering=[('Rank by Number of Rare Words', {"freq_list": "wordfreq_list", "rank_threshold": 3000, "window_start": -5, "window_end": 5})])
n2 = n1.add_subset_node(("Select by Rank", {}))


from flexiconc import Concordance
c = Concordance()
c.retrieve_from_clic(query=["stomach"], corpora="dickens")
c.add_annotation(("Annotate with Sentence Transformers",{}))
print(c.root.schema_for("Flat Clustering by Embeddings"))