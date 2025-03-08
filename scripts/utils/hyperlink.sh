function hyperlink() {
  local label="$1"
  local url="$2"

  # https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda#quick-example
  printf '\e]8;;%s\e\\%s\e]8;;\e\\\n' "$url" "$label"
}
export hyperlink
