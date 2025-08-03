
import xiaothink.llm.inference.test as test

#import xiaothink.llm.inference.test as test
#form


import re
from xiaothink.llm.inference.vision_api import *

def to_vector(img_path, vocab, use_patch=True):
    """测试压缩和解压流程"""
    # 压缩
    compressed = image_to_compressed(encoder, img_path, vocab, patch=use_patch)
    #print(f"压缩后的特征长度: {len(compressed)} 字符")
    #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
    return (compressed)
def to_img(vec, vocab, use_patch=True):
    """测试压缩和解压流程"""
    # 压缩
    compressed = compressed_to_image(decoder, vec, vocab, patch=use_patch)
    #print(f"压缩后的特征长度: {len(compressed)} 字符")
    #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
    return (compressed)
    


vocab, n_min, n_max, vocab_size = None, None, None, None
autoencoder, encoder, decoder = None, None, None

def replace_img(text, v_path, imgzip_model_path):
    # 检查文本中是否包含完整的<img>标签
    if not '<img>' in text or not '</img>' in text:
        return text
    
    # 加载模型（如果尚未加载）
    global autoencoder, encoder, decoder, vocab, n_min, n_max, vocab_size
    if autoencoder is None:
        
        autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model(imgzip_model_path))
    if vocab is None:
        vocab, n_min, n_max, vocab_size = load_vocab(v_path)
        
    # 正则表达式匹配<img>标签及其内容
    # 匹配模式：<img>任意字符（非贪婪模式）</img>
    pattern = r'<img>(.*?)</img>'
    
    # 定义替换函数：在路径后添加'666'
    def add_suffix(match):
        path = match.group(1)
        return f'<img>{to_vector(path, vocab,use_patch=False)}</img>'
    
    # 执行替换
    modified_text = re.sub(pattern, add_suffix, text)
    
    return modified_text





class QianyanModel:
    def __init__(self,ckpt_dir=r'E:\小思框架\论文\ganskchat\ckpt_test_40_3_1_t1_cloud',
               MT=40.31,
                 vocab=r'E:\小思框架\论文\ganskchat\vocab_lx3.txt',
                 imgzip_model_path=None):
        self.model,self.d=test.load(ckpt_dir=ckpt_dir, model_type=MT,
                                    vocab=vocab)
        self.imgzip_model_path=imgzip_model_path
        self.v_path=vocab
        self.his=''

    def chat_SingleTurn(self,t,temp=0.8,maxlen=1200,window=2048,
                        form=1,ontime=True,loop=True,stop=None):#0.85
        t=replace_img(t,self.v_path,imgzip_model_path=self.imgzip_model_path)
        if form==0:
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   ]
        elif form==1:
            inp='{"conversations": [{"role": "user", "content": {inp}}, {"role": "assistant", "content": "'.replace('{inp}',t)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            
            return '-1: form error'
        if stop:
            stopc.append(stop)
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
        if loop:
            inf=test.generate_texts_untilstr_loop
        else:
            inf=test.generate_texts_untilstr
            
        #print(funct)
        re=inf(self.model, self.d, inp,num_generate=maxlen,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc,
                                window=window
                                    #q=[0.6,0.4]
                                    )
        self.model.reset_states()
        return re

    def add_his(self,q,a,form=1):#0.85
        q=replace_img(q.replace('\n','\\n'),self.v_path,imgzip_model_path=self.imgzip_model_path)
        a=replace_img(a.replace('\n','\\n'),self.v_path,imgzip_model_path=self.imgzip_model_path)
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',q)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',q)


            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'

        re=a
        if form==0:
            self.his+=re
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',re)
      
        return re
    
    def chat(self,text,temp=0.68,max_len=150,form=1,ontime=True,window=2048,
             loop=True,pre_text='',repetition_penalty=1.2):
        text=replace_img(text.replace('\n','\\n'),self.v_path,imgzip_model_path=self.imgzip_model_path)
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',text)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',text)

            #print(self.his)
            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
            print('\n【实时输出】')
        #print(funct)
        if loop:
            inf=test.generate_texts_untilstr_loop
        else:
            inf=test.generate_texts_untilstr
        re=pre_text+inf(self.model, self.d, inp+pre_text,num_generate=max_len,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc,
                        window=window,
                        repetition_penalty=repetition_penalty
                                    #q=[0.6,0.4]
                                    )
        if form==0:
            self.his+=re
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',re)
      
        return re
    

    def clean_his(self):
        self.his=''


