class CodeGenerator:
    def run(self, state):
        """
        Generates code when the user intent is 'code'.
        Writes output to state.generated_code
        """

        if state.intent != "code":
            return

        prompt = state.user_input.lower()
        if "hello" in prompt:
            code = (
                'def main():\n'
                '    print("Hello, World!")\n\n'
                'if __name__ == "__main__":\n'
                '    main()\n'
            )
        else:
            code = (
                'def main():\n'
                '    print("Generated code placeholder")\n\n'
                'if __name__ == "__main__":\n'
                '    main()\n'
            )

        state.generated_code = code
