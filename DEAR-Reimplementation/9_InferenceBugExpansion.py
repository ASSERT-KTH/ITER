from transformers import pipeline

if __name__ == '__main__':
    inferenceList=['Chart14','Chart16','Chart19','Cli34','Closure4','Closure4','Closure78','Closure79','Closure106','Closure109','Closure115','Closure131','Codec1','Lang7','Lang27','Lang34','Lang35','Lang41','Lang47','Lang60','Math1','Math4','Math22','Math24','Math35','Math43','Math46','Math62','Math65','Math71','Math77','Math79','Math88','Math90','Math93','Math98','Math99']
    for bug in inferenceList:
        InferencePair = './data/'+bug+'/expansion.csv'
        
        if not os.path.exists(InferencePair):
            continue
        with open(InferencePair,'r') as infer:
            inferLines = infer.readlines()
            for line in inferLines:
                text = line.replace('\n','')              
                classifier = pipeline("sentiment-analysis", model="DEAR_BERT_Expansion_Predition_Modle/checkpoint-400")
                result = classifier(text)
                print(result[0])
                predicationLabel = result[0]['label']
                if predicationLabel in 'POSITIVE':
                    with open('./data/'+bug+'/FinalFL.csv','a') as pred:
                        pred.write(text+'\t'+str(result[0])+'\n')  
               
                    
                    
                    
                    