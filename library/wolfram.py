import wolframalpha
import sqlite3
import re

WOLFRAM_TOKEN = ''

def main(text, job_id, *args, **kwargs):
    conn = sqlite3.connect('kevin.db')
    comp1 = re.compile("[\,\.\'\";\!]")
    comp2 = re.compile("kevin", re.IGNORECASE)
    text = comp1.sub("", comp2.sub("", text.encode("ascii", errors='ignore'))).strip()
    client = wolframalpha.Client(WOLFRAM_TOKEN)

    ret = client.query(text)
    results = ''
    if len(ret.pods) > 0:
        for r in ret.results:
            results += "\n" + r.text
        # IF THERE ARE NO RESULT PODS PRINT OUT SOME OF THE PODS
        if len(results) <=0:
            for x in range(0, len(ret.pods)):
                if x < 3:
                    results += "\n" + ret.pods[x].text
                else:
                    break
    else:
        results = google_search(text)
        results += "\nSQUAAAAWWKKK! SQUAAAAWWKKK! SQUAAAAWWKKK!"
        # SEND THE SQUAKS
    with conn:
        conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?)", (job_id, results))
        conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
        conn.commit()

def google_search(query):
    import requests
    requests.packages.urllib3.disable_warnings()
    results = ''
    r = requests.get('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=' + query)
    result = r.json()

    # Print it all out
    for index, result in enumerate(result['responseData']['results']):
        results += "{}) {}\n{}\n".format(index+1, result['titleNoFormatting'], result['url'])
        index += 1

    return results
