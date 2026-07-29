function gc --argument-names msg
    if test -z "$msg"
        echo "Commit message is required"
        return 1
    end
    git add .
    git commit -m "$msg"
    git push -u origin --tags
    git push
end
