import state

def main() -> None:
    completion = state.openai.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {
                "role": "user",
                "content": """
                Give a list of genres for a movie, with a given description. I want you to return the output in a point list of genres.
                The movie description is as follows:
                While working underground to fix a water main, Brooklyn plumbers—and brothers—Mario and Luigi are transported down a mysterious pipe and wander into a magical new world. But when the brothers are separated, Mario embarks on an epic quest to find Luigi.
                """
            }
        ]
    )

    print(completion.choices[0].message.content)

if __name__ == '__main__':
    main()