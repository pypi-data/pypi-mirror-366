# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
#ENTRYPOINT []

# Run the FastAPI application by default
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
#CMD ["fastapi", "dev", "--host", "0.0.0.0", "src/uv_docker_example"]
EXPOSE 8000
CMD ["uv", "run", "mcp_stdio"]

# # Utilise l'image uv comme base avec debian
# FROM ghcr.io/astral-sh/uv:debian

# # Définit le répertoire de travail
# WORKDIR /app

# # Configure l'environnement pour uv
# ENV UV_COMPILE_BYTECODE=1
# ENV UV_LINK_MODE=copy

# # Copie les fichiers de configuration des dépendances
# COPY pyproject.toml uv.lock ./

# # Installe les dépendances en utilisant uv
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --frozen --no-install-project

# # Copie le code source
# COPY . .

# # Ajoute le src au PYTHONPATH
# ENV PYTHONPATH=/app/src

# # Installe le projet en mode editable
# RUN uv sync --frozen

# # Expose le port par défaut (ajuste selon tes besoins)
# EXPOSE 8000

# # Commande par défaut
# CMD ["uv", "run", "mcp_sse"]
