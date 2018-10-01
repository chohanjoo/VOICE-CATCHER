
#해당 문자열이 캘린더를 등록하기 위한 명령어인지를 체크해준다.
def check_calendar(sentence):
    from konlpy.tag import Okt

    okt = Okt()
    list = okt.pos(sentence)
    print(list)

    CHECK = {"캘린더", "불러와","불러","불러와줘"}
    cnt = 0

    #입력된 문자열에서 CHECK 리스트에 있는 문자열이 2개 있는지 체크
    #2개 있다면 캘린더를 등록하라는 명령어인지를 인지
    for tmp in list:
        if tmp[0] in CHECK:
            cnt += 1

    print(cnt)
    return cnt

#입력된 문자열를 파싱하여 구글 캘린더 api 호출
def input_calendar(sentence):
    from src.minah import minah
    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    string = ''
    string2 = ''
    for original_text, date in minah.parse(sentence):
        print('date : %s'%date)
        #상대 날짜인 문자열을 표준 시간으로 바꿔준다.
        string = str(date)

    print('split : %s'%string.split(' '))
    temp = string.split(' ')

    #표준 시간을 google calendar api에서 요구하는 format으로 맞춰준다.
    #일정 시작 시간
    string = temp[0] + 'T' + temp[1] + '+09:00'
    print('string : %s'%string)

    #일정이 지속되는 시간은 1시간으로 고정이다.
    # 1을 다른 숫자로 바꾸면 일정 지속시간을 수정할 수 있다.
    change = int(temp[1][1]) + 1
    temp[1] = temp[1][:1] + str(change) + temp[1][2:]

    #일정 끝 시간
    string2 = temp[0] + 'T' + temp[1] + '+09:00'
    print(string2)

    #약속 대상은 None이 defualt 값이다.
    string3 = 'None'
    words = sentence.split(' ')
    count = -1
    
    #약속 대상이 입력됬는지 확인하여 약속 대상이 있다면 string3에 대입
    for i in range(len(words)):
        if '와' in words[i]:
            string3 = words[i][:-1]
            if len(string3) == 0:
                count = i

    if count !=-1:
        string = words[i-1]

    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    CAL = build('calendar', 'v3', http=creds.authorize(Http()))

    TIMEZONE = 'America/Los_Angeles'
    
    #약속 날짜와 대상을 EVENT에 등록
    EVENT = {
        'start': {"dateTime": "%s" % string},
        'end': {"dateTime": "%s" % string2},
        'summary': '%s'%string3
    }
    #google calendar api를 호출하여 일정 등록
    event = CAL.events().insert(calendarId='primary', body=EVENT).execute()