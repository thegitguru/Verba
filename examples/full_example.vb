note this program asks for a name and age, then greets the user.

define greet person needing name, age as follows.
    say hello and name.
    if age is less than 18, do the following.
        say you are a minor.
    otherwise do the following.
        say you are an adult.
    end if.
end define.

ask the user quote what is your name and save to username.
ask the user quote how old are you and save to user age.

run greet person with username, user age.

let counter be the number 1.
keep doing the following while counter is at most 3.
    say counting and counter.
    increase counter by 1.
end keep.

say goodbye.
