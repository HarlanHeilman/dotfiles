function smiles --argument-names smiles_str
    if not type -q obabel
        echo "obabel not found. Install with: brew install open-babel"
        return 1
    end

    set -l svg (obabel -:"$smiles_str" -o svg 2>/dev/null)
    set -l inchi (obabel -:"$smiles_str" -o inchi 2>/dev/null)
    set -l flattened_svg (string join '' (string split \n -- $svg))

    set -l output "\"image\" : \"$flattened_svg\",\n\"SMILES\": \"$smiles_str\",\n\"InChI\" : \"$inchi\","
    echo $output

    if test "$_OS" = macos
        echo $output | pbcopy
    else if type -q xclip
        printf '%b' $output | xclip -selection clipboard
    else if type -q xsel
        printf '%b' $output | xsel --clipboard --input
    else
        echo "No clipboard utility found"
        return 0
    end
    echo "JSON output copied to clipboard"
end
