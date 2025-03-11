exaple_podcast_promps = """ 
<speak>
  <p><emphasis level="moderate">Hello and welcome to "Wild Wonders"—the podcast where we explore the amazing world of animals!</emphasis> I’m Lisa, your host, and today we have a fascinating episode lined up just for you.</p>
  <p><emphasis level="moderate">Have you ever wondered how octopuses change color in an instant? Or why elephants have such incredible memories?</emphasis> Well, today, we’re diving into some of the most mind-blowing animal facts that will leave you amazed!</p>
  <p>Let’s start with one of the ocean’s most mysterious creatures—the octopus. These intelligent animals can change their color and texture in the blink of an eye! This is thanks to tiny pigment cells in their skin called <phoneme alphabet="ipa" ph="krəˈmædəˌfoʊrz">chromatophores</phoneme>. Scientists believe they use this ability for camouflage, communication, and even expressing emotions!</p>
</speak>
"""

from llm.text_to_speech import ElevenLabsTextToSpeech

def main():
    print(ElevenLabsTextToSpeech(exaple_podcast_promps, "example/test"))
    
if __name__ == "__main__":
    main()