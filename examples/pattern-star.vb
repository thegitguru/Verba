let asterisk be the word *.

define print triangle needing rows as follows.
    let row be the number 1.
    keep doing the following while row is at most rows.
        let stars be a list of x.
        remove x from stars.
        let col be the number 1.
        keep doing the following while col is at most row.
            add asterisk to stars.
            increase col by 1.
        end keep.
        for each item in stars, do the following.
            display item.
        end for.
        say.
        increase row by 1.
    end keep.
end define.

ask the user quote how many rows do you want and save to row count.

run print triangle with row count.