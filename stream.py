import streamlit as st
import requests
import time
import csv
import pandas as pd
import tqdm
import json

class Doubao:
    def __init__(self, api_key, url_base, model_id):
        self.model = model_id
        self.api_key = api_key
        self.url_base = url_base
        self.history = []
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.api_key}'}
        self.kwargs = {'temperature':0.7,'max_tokens':250}
    def get_headers(self):
        return {
            'Authorization': f"Bearer {self.KEY}",
            'Content-Type': "application/json",
        }
    def myrequest(self, prompt, model, max_length=250):
        url = self.url_base
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_length
        }
        response = requests.post(url, headers=self.headers, json=data)
        time.sleep(0.3)
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
        return response.json()
    
    def inspect_history(self, n=1):
        return self.history[-n:]
    
    def __call__(self, prompt, max_tokens = 250, n = 1, temperature = 100):
        kwargs=self.kwargs
        temperature = kwargs.get('temperature', 0.7)
        response = self.myrequest(prompt, self.model, max_tokens)
        self.history.append({"question": prompt, "response":response['choices'][0]['message']['content']})

        return response['choices'][0]['message']['content']  # 根据API响应结构解析答案

URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_ID = "ep-20240803121242-nq5gj"
KEY = "f7101244-6fca-4de0-a4a9-44a3771287d8"
doubao = Doubao(api_key=KEY, url_base=URL,model_id=MODEL_ID)


# prompt1负责【积分获取&使用】方面节点判别
prompt1 = '''#Role：你的身份是招聘网站的人工智能客服。
#Background：需要分析客户输入的chat文本内容，从中分析客户表现的意图，并根据给出的分类方式，将其归类。注意在表述中，平台上使用的“豆豆”即为积分的意思。
#Workflow：根据用户给出的chat内容依次回答以下问题并将各步判断结果记录为对应变量，判断以下各变量的答案为“是”或“否”，“是”与“否”分别对应为1或0,最后输出指定格式的内容：
1. 判断用户是否明确表明想获取更多积分，如“怎么得积分”、“充值积分”、“做任务获取积分”（注意：“退回积分/返还积分/返还投诉的积分”不属于获取积分！）可选项：[1,0]，判断结果赋值为gain；
    1.1.判断用户是否有充值的意向，如“怎么充值”、“获取充值积分”，可选项：[1,0]，判断结果赋值为charge；
    1.2.判断用户是否邀请好友或推荐好友注册，可选项：[1,0]，判断结果赋值为advise；
    1.3.判断用户是否明确表示已完成任务，可选项：[1,0]，判断结果赋值为mandate；
    1.4.判断用户是否明确表示未获得奖励积分，例如“邀请过好友没给积分”、“拉了三个新人为什么没给我积分”，可选项：[1,0]，判断结果赋值为dont_gain；
2. 用户是否咨询花费积分的规则，仅限于类似“打一次电话/发一次招聘消耗多少积分”、“联系一次老板要花多少钱/积分”的描述，（注意：“未接通/未打通还扣积分”不属于咨询积分花费规则的范畴），可选项：[1,0]，判断结果赋值为use；
3. 用户是否明确表示充值的积分不见了，例如“充值的积分不见了”、“我的积分不见了”，可选项：[1,0]，判断结果赋值为disapp；
4. 用户明确提及积分使用故障、积分无法正常使用、如“积分用不了”，可选项：[1,0]，判断结果赋值为cannot_use；
5. 用户是否提及临时积分与有效期问题，例如”临时积分过期、无法使用”，可选项：[1,0]，结果赋值为interim；
6. 用户是否咨询充值/正式积分的有效期相关问题，如“积分会过期吗”、“正式积分有效期多久”，可选项：[1,0],结果赋值为validity;
7. 用户是否表示想要转移积分，例如“怎么将积分转到另一个账号”、“移动积分”，可选项：[1,0],结果赋值为move;
7. 用户是否明确表示想要开发票，可选项：[1,0]，判断结果赋值为purchase；
9. 用户明确表示某信息或某用户的内容涉及歧视、违法或违规信息，（注意：“信息虚假，内容与实际不符”不属于违法违规）可选项：[1,0]，判断结果赋值为illegal。
#output
对以上各个方面的问题进行判断，需要关注上诉描述内容的括号中的注意事项，区分各类标签的细节，根据各问题的输出结果，严格按照以下json格式进行输出：
{
"gain": gain,
"charge": charge,
"advise":advise,
"mandate":mandate,
"dont_gain":dont_gain,
"use": use,
"disapp": disapp,
"cannot_use":cannot_use,
"interim":interim,
"validity":validity,
"move": move,
"purchase": purchase,
"illegal":illegal
}
# 实例example：
输入chat："[用户: 推荐朋友注册了，怎么没送积分,用户: 19060905603]"
输出json内容:"{
"gain": 1,
"charge": 0,
"advise":1,
"mandate":0,
"dont_gain":1,
"use": 0,
"disapp": 0,
"cannot_use":0,
"interim":0,
"validity":0,
"move": 0,
"purchase": 0,
"illegal":0
}"
输入chat："[用户: 上次打电话投诉要退的积分还没还，积分什么时候还我、退还我积分]"
输出json内容:"{
"gain": 0,
"charge": 0,
"advise":0,
"mandate":0,
"dont_gain":0,
"use": 0,
"disapp": 0,
"cannot_use":0,
"interim":0,
"validity":0,
"move": 0,
"purchase": 0,
"illegal":0
}"
现给出chat如下，请按照上面给出的方法进行分析，并输出指定格式的json内容，严格遵循格式要求，禁止输出分析过程。
输入chat=
'''


# prompt2 主要负责【扣积分&退积分&积分退款】方面的节点的判定
prompt2 = '''#Role：你的身份是招聘网站的人工智能客服。
#Background：需要分析客户输入的chat文本内容，从中分析客户表现的意图，并根据给出的分类方式，将其归类。
#Workflow：根据用户给出的chat内容依次回答以下问题并将各步判断结果记录为对应变量，判断以下各变量对应为1或0,最后输出指定格式的内容：
1. 判断用户是否明确表示被平台扣除了积分，如“没打电话还扣我积分”、“怎么一下扣我3分”、“扣的积分退我”都说明用户账户中的积分被扣了，可选项：[1,0]，判断结果赋值为result；
2. 用户明确提及退积分，希望返还/退回积分，如“我要退积分”、“积分还没退”、“把积分退了”等，可选项：[1,0]，判断结果赋值为return；
3. 用户明确表示积分还没退或催促退回积分，注意不是“我要退积分”、“给我退积分”这种首次申请退积分的要求，而是如“投诉的积分还没返还”、“积分还没退还”、“积分什么时候才退”、“积分未退”等，可选项：[1,0]，判断结果赋值为not_return；
4. 用户明确要求积分退款或退款，要求返还充值的金额，可选项：[1,0]，判断结果赋值为return_m；
5. 用户明确表示“没拨打电话”、“不打电话”、“没联系”或“未点击拨打”（“没打通”表示已拨打但未打通），注意区分“没联系”不等于“没联系上”，可选项：[1,0]，判断结果赋值为call;
    5.1. 用户表示没打通对方的电话，包括未接听、被挂断、空号、通话中、占线、关机等情况下的打不通，如“没联系上”、“打不通”，可选项：[1,0]，判断结果赋值为call_failed；
    5.2. 用户明确表示没谈成工作，可选项：[1,0]，判断结果赋值为final；
    5.3. 用户反馈信息虚假或信息描述与实际不符（说明电话已打通），可选项：[1,0]，判断结果赋值为fake_info；
    5.4. 用户提及拨打对象已招满、停止招聘或者不招工作了（说明电话已打通），可选项：[1,0]，判断结果赋值为full_or_not;
6. 判断用户是否提及投诉，如“投诉的积分”、“我要投诉”，可选项：[1,0]，判断结果赋值为complain；
    6.1. 判断用户是否已经完成投诉，如“投诉的积分还没返”、“投诉了积分什么时候退还”表示已投诉。注意：“我要投诉/怎么投诉”表示还未进行投诉！可选项：[1,0]，判断结果赋值为have_complained;
#output
对以上各个方面的问题进行判断后，严格按照以下json格式进行输出：
{
"result": result,
"return": return,
"not_return": not_return,
"return_m": return_m,
"call": call,
"call_failed": call_failed,
"final": final,
"fake_info": fake_info,
"full_or_not": full_or_not,
"complain": complain,
"have_complained":have_complained
}
#example
输入chat："[用户: 电话正在通话中&nbsp; 没有跟老板通上话也扣积分？？]"
输出json："{
"result": 1,
"return": 0,
"not_return": 0,
"return_m": 0,
"call": 1,
"call_failed": 1,
"final": 0,
"fake_info": 0,
"full_or_not": 0,
"complain": 0,
"have_complained":0
}"
输入chat："[用户: 投诉，用户: 我电话都没打通，用户: 我要退积分]"
输出json："{
"result": 0,
"return": 1,
"not_return": 0,
"return_m": 0,
"call": 1,
"call_failed": 1,
"final": 1,
"fake_info": 0,
"full_or_not": 0,
"complain": 1,
"have_complained":0
}"
现给出chat如下，请按照上面给出的方法进行分析，并输出指定格式的json内容，严格遵循格式要求，禁止输出分析过程。
输入chat=
'''



# prompt负责完成对【用户身份】的识别
prompt3 = '''#Role：招工软件鱼泡网的优秀智能客服
#Gole：通过分析用户与客服的对话信息，从对话中识别该用户在平台上的身份，身份可能为"老板","工人"或"未知"，设置选项为["A","B","C"]。注意！仅能从给出的选项中取值。
#Background：
### 1.在该平台上的用户有‘工人身份’和‘老板身份’两类人，平台上求职者、工人、工友、找活的人为‘工人’，也称‘牛人’，招聘者、找工人的人称为‘老板’,部分情况下，用户输出会说明自己是“求职者”或“招聘者”。
### 2.平台上，工人与老板都可以通过花费积分，获得拨打电话联系对方的机会，老板浏览工人们的简历信息、工人们浏览老板发布的招聘信息，工人与老板都可以进行投诉、申请退积分、打电话、打不通电话。
### 3.若信息中未涉及能代表身份的词或行为、无法明确判断身份，则判定其身份为“未知”，仅在有具体证据或线索时可判定用户为“老板”或“工人”。
### 4.工人专属行为与描述：发布\修改\关闭\删除简历、找活、联系老板、“招满了退积分”、“对方招满了，要求返还积分”、投诉老板信息虚假、老板电话打不通、“购买找活会员”、“购买求职会员”.
### 5.老板专属行为：发布\修改\关闭\删除职位信息或招聘信息、联系工人、投诉工人信息虚假、工人电话打不通、购买招聘会员、招聘牛人、“招满了怎么关闭招聘信息”、“怎么停止招聘”.
### 6.未知身份：若只提供如下描述如“电话打不通”、“投诉的积分为什么没有返还”、“信息虚假”、“打不通为什么还要扣积分”、“要求返还积分”，而没有其他含有身份信息的内容，并不能判断出用户的身份。
## 注意！chat中没有提及关于身份信息的线索时，均认为该用户身份为“未知”,对应答案为“C”。
#output：参考上述给出的判断条件，通过用户给出的chat判断用户在平台上身份，字母"A","B","C"分别代表"老板","工人","身份未知"，从["A","B","C"]中取值赋给变量identity，没有提及任何关于身份的线索信息时，并以下述json格式进行输出：
{
"identity":identity
}
输入chat："[用户: 打不通为什么还要扣积分，用户: 投诉的积分为什么没有返还]"
输出：{
"identity": "C"
}
输入chat："[用户: 打电话不接，退积分、用户: 我前面的投诉的积分么给我退]"
输出：{
"identity": "C"
}
输入chat："[用户: 今天打了电话打通了人招满了投诉到现在积分没有退人家信息之接下架]"
输出：{
"identity": "B"
}
输入chat："[用户: 查看简历投诉积分未退还]"
输出：{
"identity": "A"
}
输入chat："[用户: 已找满信息不下架扣我积分不退、用户: 已招满为什么不关、用户: 己招满怎样退积分]"
输出：{
"identity": "B"
}
输入chat："[用户:打不通为什么还要扣积分、用户:求职者]"
输出：{
"identity": "B"
}
输入chat："[用户:打不通为什么还要扣积分、用户:招聘者、用户:您好我充了会员用不了]"
输出：{
"identity": "A"
}
参考上面的样例内容，严格按照以上格式要求输出json结果，禁止输出分析过程等内容，现给出用户输入chat='''


def get_info(x):
    try:
        res=list(json.loads("{"+x.replace('，',',').split("{")[1].split("}")[0]+"}").values())
        return res
    except:
        return None


####################################
# 通过组合各种情况给出【积分获取&使用】的标签
def use_part1(l1):    #l1为class_data['part1']中内容 ,格式为List[int]
    if l1==[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        return "010000"
    if l1[0]==1:
        if l1[1]==1:
            return "010101"
        elif l1[2]==1 and l1[4]==1:
            return "010102"
        elif l1[3]==1 and l1[4]==1:
            return "010103"
        else:
            return "010100"
    if l1[1]==1:
        return "010000"
    elif l1[2]==1 and l1[4]==1:
        return "010101"
    elif l1[3]==1 and l1[4]==1:
        return "010103"
    if l1[4]==1:
        return "010103"
    if l1[6]==1:
        return "010202"
    if l1[5]==1:
        return "010201"
    if l1[7]==1:
        return "010203"
    if l1[8]==1:
        return "010207"
    if l1[9]==1:
        return "010204"
    if l1[10]==1:
        return "010205"
    if l1[11]==1:
        return "010206"
    if l1[12]==1:
        return "010300"
    else:
        return "010000"       


#############################
# 通过组合各种情况给出【扣积分&退积分&积分退款】的标签
# l1格式为List[int]，对应class_data['part2']中的内容，l3格式要求为str
def use_part2(l1,l3):
    if l1==[0,0,0,0,0,0,0,0,0,0,0]:
        return "000000"
    if l1[0]==1:     #被扣了积分
        if l1[2]==1:   #积分还没退
            if l1[9]==l1[10]==1:  #已投诉积分仍未退
                if l3=='A':
                    return "000601"
                elif l3=='B':
                    return "000602"
                else:
                    return "000600"
            elif l1[3:]==[0,0,0,0,0,0,0,0]:
                return "000600"
        if l1[1:]==[1,0,0,0,0,0,0,0,0,0]:
            return "000400"   
        if l1[5]==1:
            return "000302"
        if l1[8]==1:
            if l3=="A":
                return "000305"
            elif l3=="B":
                return "000306"
            else:
                return "000306"
        if l1[6]==1:
            return "000307"
        if l1[7]==1:
            return "000308"
        if l1[4]==1:     #未拨打电话
            return "000301"
        if l1[1:]==[0,0,0,0,0,0,0,0,0,0]:
            return "000300"  
    if l1[1]==1:    #退积分
        if l1[2]==1:   #积分还没退
            if l1[10]==1:  #已投诉积分仍未退
                if l3=='A':
                    return "000601"
                elif l3=='B':
                    return "000602"
                else:
                    return "000600"
            elif l1[3:12]==[0,0,0,0,0,0,0,0]:
                return "000600"    
        if l1[5]==1:
            if l3=="A":
                return "000403"
            elif l3=="B":
                return "000404"
            else:
                return "000402"
        if l1[6]==1:
                return "000407"   
        if l1[7]==1:
            return "000408"
        if l1[8]==1:
            if l3=="A":
                return "000405"
            elif l3=="B":
                return "000406"
            else:
                return "000406"
        if l1[4]==1:
            return "000401"
        if l1[9]==1:
            return "000400"
        elif l1[2:]==[0,0,0,0,0,0,0,0,0]:
            return "000400"
        elif l1[3]==1:
            return "000500"
    if l1[2]==1:   #积分还没退
        if l1[10]==1:
            return "000600"
        else:
            return "000600"
    if l1[3]==1:
        return "000500"
    if l1[4]==0:    #拨打了电话
        if l1[5]==1:   #没打通
            if l3=="A":
                return "000203"
            elif l3=="B":
                return "000204"
            else:
                return "000202"
        else:    #打通了
            if l1[7]==1:     #信息虚假
                if l3=="A":
                    return "000209"
                elif l3=="B":
                    return "000210"
                else:
                    return "000208"
            if l1[8]==1:     #招满
                if l3=="A":
                    return "000205"
                elif l3=="B":
                    return "000206"
                else:
                    return "000208"
            if l1[6]==1:
                return "000207"
            if l1[9]==1 and l1[10]==0:
                if l3=='A':
                    return "000101"
                elif l3=='B':
                    return "000102"
                else:
                    return "000100"
    if l1[7]==1:     #信息虚假
        if l3=="A":
            return "00209"
        elif l3=="B":
            return "000210"
        else:
            return "000208"
    if l1[8]==1:     #招满
        if l3=="A":
            return "000205"
        elif l3=="B":
            return "000206"
        else:
            return "000208"
    if l1[6]==1:
        return "000207"
    if l1[9]==1 and l1[10]==0:
        if l3=='A':
            return "000101"
        elif l3=='B':
            return "000102"
        else:
            return "000100"
    else:
        return "000000"      

code1 = ['000000', '000100', '000101', '000102', '000201', '000202', '000203', '000204', '000205', '000206', '000207', '000208', '000209', '000210', '000300', '000301', '000302', '000303', '000304', '000305', '000306', '000307', '000308', '000309', '000310', '000400', '000401', '000402', '000403', '000404', '000405', '000406', '000407', '000408', '000409', '000410', '000500', '000600', '000601', '000602']
label1 = ['无', '我要投诉', '我要投诉工人', '我要投诉老板', '未拨打电话', '电话打不通', '工人电话打不通', '老板电话打不通', '工人不找工作', '老板招满不招', '没谈成工作', '信息虚假', '工人求职信息虚假', '老板招聘信息虚假', '扣积分', '未拨打电话，扣积分', '电话打不通，扣积分', '工人电话打不通，扣积分', '老板电话打不通，扣积分', '工人不找工作，扣积分', '老板招满不招，扣积分', '没谈成工作，扣积分', '信息虚假，扣积分', '工人求职信息虚假，扣积分', '老板招聘信息虚假，扣积分', '退积分', '未拨打电话，退积分', '电话打不通，退积分', '工人电话打不通，退积分', '老板电话打不通，退积分', '工人不找工作，退积分', '老板招满不招，退积分', '没谈成工作,退积分', '信息虚假，退积分', '工人求职信息虚假，退积分', '老板招聘信息虚假，退积分', '退款，积分退款', '积分仍未退', '已投诉工人，积分仍未退', '已投诉老板，积分仍未退']

code2 = ['010000', '010100', '010101', '010102', '010103', '010201', '010202', '010203', '010204', '010205', '010206', '010207', '010208', '010300']
label2 = ['无', '获取积分', '充值积分', '邀请好友未获得积分', '完成任务未获得积分', '积分消耗问题', '积分消失、无故减少', '积分异常、使用故障', '积分有效期', '积分转移', '积分开票', '临时积分', '积分不能用', '信息违法']

dict1 = {i:j for i,j in zip(code2,label2)}

dict2 = {i:j for i,j in zip(code1,label1)}


# 定义处理字符串的函数
def process_string(input_string):
    # 这里可以放置你的处理逻辑
    # 例如，将字符串反转
    processed_string = input_string[::-1]
    return processed_string

# 大模型意图识别提示词
#st.code(prompt1, language='python')
#st.code(prompt2, language='python')
#st.code(prompt3, language='python')

# 设置网页标题
st.title('AI客服实现用户意图识别项目')

st.text('设置接收时间为10s每轮，确保每轮不会一次性提供太多意图')
st.text('下面代码运行时间稍微有点长，15s左右，请耐心等待......')
user_input = st.text_input("请输入要判定的chat",key = 'input1')

# 当用户输入字符串并点击按钮时，处理字符串并显示结果
if st.button("处理字符串"):
    if user_input:
        a,b,c = doubao(prompt1+user_input),doubao(prompt2+user_input),doubao(prompt3+user_input)
        ans1 = get_info(a)
        ans2 = get_info(b)
        ans3 = json.loads("{"+c.replace('，',',').split("}")[0].split("{")[-1]+"}")['identity']
        st.text_area("中间结果", value=f"part1判定：{ans1}\npart2判定：{ans2}\npart3判定：{ans3}\n",height=60, key="temp_result")
        p1_ans = dict1[use_part1(ans1)]
        p2_ans = dict2[use_part2(ans2,ans3)]
        st.text_area("中间结果2", value=f"part1编码：{use_part1(ans1)}\npart2编码：{use_part2(ans2,ans3)},height=60, key="temp_result2")
        result_text = f"处理结果：\n积分充值获取与使用问题：{p1_ans}\n积分投诉退款问题：{p2_ans}"
        st.text_area("处理结果", value=result_text, height=100, key="result_text")
    else:
        st.warning("请输入字符串")
#st.code("prompt1 = '''"+prompt1+"'''", language='python')
#st.code("prompt2 = '''"+prompt2+"'''", language='python')
#st.code("prompt3 = '''"+prompt3+"'''", language='python')

#展示映射表
st.text("获取积分、积分使用类")
df1 = pd.DataFrame({"code":code2,"label":label2})
st.dataframe(df1.style.highlight_max(axis=0))
st.text("投诉退分退款类")
df2 = pd.DataFrame({"code":code1,"label":label1})
st.dataframe(df2.style.highlight_max(axis=0))
