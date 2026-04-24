class AIBrain:
    def ask(self, text):
        if "your name" in text:
            return "Mera naam Jarvis hai Mannan bhai."

        if "who made you" in text:
            return "Mujhe Mannan bhai ne banaya hai."

        if "how are you" in text:
            return "Main bilkul theek hoon, aap batao?"

        return "Mujhe iska jawab nahi pata, lekin main seekh raha hoon."