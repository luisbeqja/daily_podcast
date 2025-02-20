from flask import Flask, jsonify, request

from llm.llm import create_episode, create_episode_lineup, create_first_episode

app = Flask(__name__)

""" @app.route('/api/podcast/first-episode', methods=['GET'])
def first_episode():
    data = request.json
    response = get_response(data["query"])
    return jsonify({"message": response}) """
    
    
podcast_topic = "Mussolini was a great leader ?"
    
podcast_lineup = """
Episode 1: Exploring the Rise of Mussolini: Charisma and Control  
\nEpisode 2: Fascism: The Ideology Behind Mussolini's Leadership  
\nEpisode 3: Mussolini's Policies: Impact on Italy's Economy and Society  
\nEpisode 4: World War II: Mussolini's Role and Decisions  
\nEpisode 5: Legacy and Controversy: Assessing Mussolini's Leadership Today"""

first_episode_script = """
`[Upbeat background music starts]
\n\nWelcome to "Leaders in History," where we dive deep into the lives of influential figures and explore their legacies. 
In today’s episode, we ask the provocative question: Was Mussolini a great leader? 
\n\nJoin us as we unpack the complexities of Mussolini’s rule over five engaging episodes. We’ll kick off with 
Episode 1, “Exploring the Rise of Mussolini: Charisma and Control,” 
followed by Episode 2, where we delve into the “Fascism: The Ideology Behind Mussolini's Leadership.” \n\nNext, in 
Episode 3, we’ll examine “Mussolini's Policies: Impact on Italy's Economy and Society,” before tackling his pivotal role in World War II in
Episode 4. Finally, in Episode 5, we’ll confront the “Legacy and Controversy” surrounding Mussolini's leadership today.
\n\nSo, buckle up as we journey through history to uncover the truth behind this polarizing figure!\n\n[Background music fades out]`
"""



@app.route('/api/podcast/episode-lineup', methods=['GET'])
def episode_lineup():
    response = create_episode_lineup(podcast_topic)
    return jsonify({"message": response})


#TEST
@app.route('/api/podcast/first-episode', methods=['GET'])
def first_episode():    
    response = create_first_episode(podcast_topic, podcast_lineup)
    return jsonify({"message": response})


@app.route('/api/podcast/episode', methods=['GET'])
def episode():
    response = create_episode(podcast_topic, 1, first_episode_script)
    return jsonify({"message": response})