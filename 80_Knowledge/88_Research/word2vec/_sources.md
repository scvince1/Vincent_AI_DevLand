# Sources — word2vec

## Primary Sources (not yet scraped)

| Planned File | Title | Author | Year | URL / DOI | Access | Tier | Status |
|---|---|---|---|---|---|---|---|
| mikolov-2013-efficient-estimation.md | Efficient Estimation of Word Representations in Vector Space | Mikolov, T., Chen, K., Corrado, G., Dean, J. | 2013 | arXiv:1301.3781 | OA | T1 | Pending |
| mikolov-2013-distributed.md | Distributed Representations of Words and Phrases and their Compositionality | Mikolov, T., Sutskever, I., Chen, K., Corrado, G., Dean, J. | 2013 | arXiv:1310.4546 | OA | T1 | Pending |
| bengio-2003-neural-language-model.md | A Neural Probabilistic Language Model | Bengio, Y., Ducharme, R., Vincent, P., Jauvin, C. | 2003 | JMLR 3:1137-1155 | OA (mirror) | T1 | Pending |
| deerwester-1990-lsa.md | Indexing by Latent Semantic Analysis | Deerwester, S., Dumais, S., Furnas, G., Landauer, T., Harshman, R. | 1990 | JASIS 41:391-407 | Paywall (UChicago) | T1 | Pending |
| bolukbasi-2016-man-programmer.md | Man is to Computer Programmer as Woman is to Homemaker? | Bolukbasi, T., Chang, K.-W., Zou, J., Saligrama, V., Kalai, A. | 2016 | arXiv:1607.06520 | OA | T1 | Pending |

## Secondary / Contextual Sources (not yet scraped)

| Planned File | Title | Author | Year | URL / DOI | Access | Tier | Status |
|---|---|---|---|---|---|---|---|
| firth-1957-synopsis.md | A Synopsis of Linguistic Theory 1930-1955 (contains "you shall know a word by the company it keeps") | Firth, J.R. | 1957 | Studies in Linguistic Analysis, Oxford (book) | Paywall (book) | T2 | Pending |
| harris-1954-distributional-structure.md | Distributional Structure | Harris, Z. | 1954 | Word 10:146-162 | Paywall (journal) | T2 | Pending |
| chomsky-1957-syntactic-structures.md | Syntactic Structures | Chomsky, N. | 1957 | Mouton (book) | Paywall (book) | T2 | Pending |
| vaswani-2017-attention.md | Attention Is All You Need | Vaswani, A., et al. | 2017 | arXiv:1706.03762 | OA | T1 | Pending (primarily for attention concept; cross-ref to word2vec evolution line) |

## Retrieval Plan

- **OA-retrievable** (via arXiv / Semantic Scholar / Unpaywall): 4 of 5 primary (Mikolov x2, Bengio, Bolukbasi), 1 of 4 secondary (Vaswani)
- **Paywall** (requires UChicago SSO manual fetch): 1 of 5 primary (Deerwester 1990 LSA), 3 of 4 secondary (Firth, Harris, Chomsky) -- these are added to `{KB_ROOT}/_todo-paywall.md`
- **Next action**: Invoke kb-builder to scrape OA sources via Workflow B. Vincent fetches paywall sources at his convenience via Workflow A.
