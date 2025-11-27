from askrun_gpt4all import load_model, model
ok,err = load_model()
print('model loaded:', ok, err)
def cb(txt):
    print('TOK['+str(len(txt))+']:' + str(txt), end='|')
try:
    model.generate('Hello. Say this slowly: How are you?', max_tokens=60, temp=0.1, streaming=True, callback=cb)
except Exception as e:
    print('\nstream failed:', e)
