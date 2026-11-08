# Codebase research: request handling

Requests enter through `src/handlers.py`. The API key is parsed in
`authenticate()`. No middleware limits requests today.
