function venv
    if not test -d .venv
        uv venv
    end
    if test -f .venv/bin/activate.fish
        source .venv/bin/activate.fish
    else
        echo "No .venv/bin/activate.fish found. Recreate the venv with: uv venv"
        return 1
    end
end
