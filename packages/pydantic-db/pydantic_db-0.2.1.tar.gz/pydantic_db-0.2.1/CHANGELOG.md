# Changelog

## v0.2.1 (released 2025-07-30)

### Bug fixes

- Handle aliased fields when generating column lists. [[d1e0e85](https://github.com/NRWLDev/pydantic-db/commit/d1e0e856b3cad3a9e50cec120adfc82040403b4d)]

## v0.2.0 (released 2025-07-25)

### Features and Improvements

- **Breaking** Drop support for python 3.9 prior to End of Life. [[a90f2fe](https://github.com/NRWLDev/pydantic-db/commit/a90f2fe4ef047909842011b755992a0efef83a47)]

## v0.1.13 (released 2025-07-25)

### Bug fixes

- Handle list fields that have been json aggregated rather than built by raw select. [[f58b2b6](https://github.com/NRWLDev/pydantic-db/commit/f58b2b65e441a01f139ef3a9a9368a79e555862d)]

## v0.1.12 (released 2025-07-25)

### Features and Improvements

- Handle ForwardRefs and circular model references. [[57eadb5](https://github.com/NRWLDev/pydantic-db/commit/57eadb5db51c2c8d78cf8fc532315ea3a6ad75a2)]

## v0.1.11 (released 2025-07-25)

### Bug fixes

- Remove incorrect breaks in model parsing that prevented multiple fields processing if a union or list was detected. [[ef29561](https://github.com/NRWLDev/pydantic-db/commit/ef29561372a688cb64c85b480d67bd5991f9be29)]

## v0.1.10 (released 2025-07-25)

### Features and Improvements

- Support flattening nested list model data to ensure uniqueness. [[b42bd14](https://github.com/NRWLDev/pydantic-db/commit/b42bd140c53e5a218154546bba67a8265c02f755)]

## v0.1.9 (released 2025-07-23)

### Features and Improvements

- Add support for joins that create duplicate rows to fetch nested list models. [[afa7ce9](https://github.com/NRWLDev/pydantic-db/commit/afa7ce94acfd115339282db8648962bbc364dbb2)]

## v0.1.8 (released 2025-07-23)

### Bug fixes

- Include base_table in nested fields when generating typed columns. [[3fac08c](https://github.com/NRWLDev/pydantic-db/commit/3fac08cf905e2e5fda46406c25a2db07323d23ff)]

## v0.1.7 (released 2025-06-11)

### Bug fixes

- Sort the return value from sortable_fields. [[1c20f31](https://github.com/NRWLDev/pydantic-db/commit/1c20f31178bc3370aa6acf7b027118a4857009ea)]

## v0.1.6 (released 2025-06-11)

### Features and Improvements

- Add support for listing sortable columns including nested fields. [[4c25959](https://github.com/NRWLDev/pydantic-db/commit/4c25959bad50914d926b55e04157b2dff5e8ee68)]

## v0.1.5 (released 2025-05-14)

### Bug fixes

- Update project description. [[969bc4d](https://github.com/NRWLDev/pydantic-db/commit/969bc4de51cc59d66fd56573a2d6e0ef07f44273)]

## v0.1.4 (released 2025-05-12)

### Features and Improvements

- Add support for optional nested models with a default primary field of id. [[e040522](https://github.com/NRWLDev/pydantic-db/commit/e040522f2c991dd95125b8eeb2c97e50166069c4)]

## v0.1.3 (released 2025-05-12)

### Bug fixes

- Update type hints to play nicer with mypy. [[3158627](https://github.com/NRWLDev/pydantic-db/commit/31586270ef99a581628c6c8959e3775451cab3c3)]

## v0.1.2 (released 2025-05-12)

### Bug fixes

- Drop documentation link from pypi. [[f1627de](https://github.com/NRWLDev/pydantic-db/commit/f1627de934151cdd05000d89b9e79033eb68dbeb)]

## v0.1.1 (released 2025-05-12)

### Bug fixes

- Add py.typed for type checkers. [[ed12f79](https://github.com/NRWLDev/pydantic-db/commit/ed12f79ff1a92f33e75b080270a566e5363cace1)]

## v0.1.0 (released 2025-05-12)

### Features and Improvements

- Add support for extracting columns and types from a model. [[f4178ae](https://github.com/NRWLDev/pydantic-db/commit/f4178ae54efffffe65da50718fffb389a21a4977)]
- Add support for nested models [[998ab19](https://github.com/NRWLDev/pydantic-db/commit/998ab191d07afaba9ad12b69671b875227a63620)]
- Basic database model mapping for result and list of results. [[f007a01](https://github.com/NRWLDev/pydantic-db/commit/f007a012c97b7b4c00eebcb1503035408e74c267)]

### Miscellaneous

- Expand tests to confirm support for sqlite [[b40c806](https://github.com/NRWLDev/pydantic-db/commit/b40c806fdb2531deece4e195f0f5eb77fea29596)]
- Expand test coverage [[b69fbe0](https://github.com/NRWLDev/pydantic-db/commit/b69fbe09a9f1f0097b53c3fa6acd77e946602d8c)]
