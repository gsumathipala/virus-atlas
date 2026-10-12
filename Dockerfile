# Hugging Face Space (Docker SDK).
#
# The atlas is built into the image rather than fetched at boot: the ICTV
# spreadsheet is downloaded once during the build, so a cold start is a
# gunicorn boot (about a second) and the container needs no network to serve
# the taxonomy. Only the live panels -- Europe PMC, WHO, UKHSA, Nextstrain --
# reach out at runtime.
FROM python:3.12-slim

# Spaces run the container as uid 1000; create that user up front so the
# build artefacts can be owned by it.
RUN useradd --create-home --uid 1000 user

WORKDIR /app

# Dependencies first, so a code change does not re-resolve the wheel set.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

# Download the current ICTV Virus Metadata Resource, bake the Natural Earth
# geometry into SVG paths, and build data/atlas.json (~37 MB, peaks near
# 300 MB). Failing here fails the build, which is the right moment to find
# out that an upstream URL has moved.
RUN python fetch_vmr.py \
 && python build_world.py \
 && python -m atlas.build \
 && chown -R user:user /app

USER user
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/user

# No persistent disk on a Space: the filesystem is restored from the image on
# every restart, so tier corrections do not survive one. This makes the
# interface say so instead of implying they are saved.
ENV EPHEMERAL_STORAGE=1

# Spaces route to 7860 by default; app_port in README.md front-matter agrees.
EXPOSE 7860

# Two workers here, unlike the single worker used on a 512 MB host: a Space
# has 16 GB, and the atlas costs ~165 MB per worker, so a second one buys
# real parallelism for JSON serialisation at a cost that does not matter.
CMD ["gunicorn", "app:app", "--workers", "2", "--threads", "4", \
     "--timeout", "120", "--bind", "0.0.0.0:7860", "--access-logfile", "-"]
