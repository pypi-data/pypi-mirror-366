import time



# Questions
Questions = [
    ["What is 6 times 7?~($10)"],
    ["Which planet is known as the Red Planet?~($10)"],
    ["Which word is a synonym for “happy”?~($10)"],
    ["What is the largest ocean on Earth?~($10)"],
    ["Who was the first President of the United States?~($10)"],
    ["What is the process by which plants make their own food?~($10)"],
    ["What is ¾ as a decimal?~($10)"],
    ["In order to make oil flow fast in a pipe oil should be...?~($10)"],
    ["Which continent is the Sahara Desert on?~($10)"],
    ["What is the boiling point of water at sea level in Celsius?~($10)"],
    ['end']
]
# options
Options = [
    ["43", "32", "42", "56"],
    ["Venus", "Mars", "Jupiter", "Saturn"],
    ["Sad", "Angry", "Joyful", "Tired"],
    ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
    ["Abraham Lincoln", "George Washington", "Thomas Jefferson", "John Adams"],
    ["Digestion", "Photosynthesis", "Respiration", "Fermentation"],
    ["0.25", "0.5", "0.75", "0.85"],
    ["Cooled", "Heated", "Expended", "Compressed"],
    ["Asia", "Africa", "Australia", "South America"],
    ["90C", "100C", "110C", "120C"],
    ['end']
]

real_answer = ['42',
               'Mars',
               'Joyful',
               'Pacific Ocean',
               'George Washington',
               'Photosynthesis',
               '0.75',
               'Heated',
               'Africa',
               '100C'
               ]

User_answers = []


# main


def main():

    print(" ")
    greet = "__Welcome to Questioning g__"
    print(greet.center(90))

    # options
    print("~Start")
    print("~Exit")

    # first input block
    f_input = input("Please enter one of options given options: ")
    f2_input = f_input.title().strip()

    # logic block

    def Start():

        score = 0
        print("""\n[NOTE: you will be asked 10 questions each question is equal to a fixed amount of prize prepare for question number 1 
              it will be asked in 10 seconds you will have only 15 seconds to answer every question. every wrong ans will decrease your score]\n""")
        print("loading Questions...\n")
        time.sleep(10)

        for i in range(len(Questions)):
            if Questions[i] == Questions[-1]:
                break
            print(Questions[i])
            time.sleep(5)

            for option in Options[i]:
                print(option)
                time.sleep(1)
            print('')
            input_answer = input("\n Enter your answer:")
            print('')
            user_answer = input_answer.title().strip()
            time.sleep(10)

            for x in range(1, len(Questions)):
                User_answers.append(user_answer)
                break
        print('\nCalculating your score...')
        prize = 100
        score = 0
        for real, user in zip(real_answer, User_answers):
            if user == real:
                score += 10
            else:
                prize -= 10

        print({f"score is {score}"})
        if score > 0:
            print({f"congratulations you won ${prize}"})
        else:
            print("you lose try again")

    match f2_input:
        case "Start":
            Start()
        case "Exit":
            print("exited with nothing")


if __name__ == "__main__":
    main()
