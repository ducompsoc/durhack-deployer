# https://stackoverflow.com/a/77663806/11045433
DIRNAME=$(dirname $( readlink -f "${BASH_SOURCE[0]:-"$(command -v -- "$0")"}" ))
export PYTHONPATH=${PYTHONPATH}:${DIRNAME}/src
