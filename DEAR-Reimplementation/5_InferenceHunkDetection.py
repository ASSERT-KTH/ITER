from transformers import pipeline

if __name__ == '__main__':
    inferenceList=['Chart14','Chart16','Chart19','Cli34','Closure4','Closure78','Closure79','Closure106','Closure109','Closure115','Closure131','Codec1','Lang7','Lang27','Lang34','Lang35','Lang41','Lang47','Lang60','Math1','Math4','Math22','Math24','Math35','Math43','Math46','Math62','Math65','Math71','Math77','Math79','Math88','Math90','Math93','Math98','Math99']
    for bug in inferenceList:
        InferencePair = './data/'+bug+'/inference.csv'
        with open(InferencePair,'r') as infer:
            inferLines = infer.readlines()
            for line in inferLines:
                text = line.split('\t')[0]
                groundTruthLabel = line.split('\t')[1]
                groundTruthLabel=groundTruthLabel.replace('\n','')
                print('groundTruthLabel',groundTruthLabel)
                classifier = pipeline("sentiment-analysis", model="DEAR_BERT_Hunk_Detection_Modle/checkpoint-10420")
                result = classifier(text)
                print(result[0])
                predicationLabel = result[0]['label']
                predicationLabel = '0' if predicationLabel in 'NEGATIVE' else '1'
                print('predicationLabel',predicationLabel)

                with open('./data/'+bug+'/prediction.csv','a') as pred:
                    pred.write(text+'\t'+str(result[0])+'\n')                 
                  
                if predicationLabel in '1':
                    with open('./data/'+bug+'/PositivePrediction.csv','a') as pred:
                        pred.write(text+'\t'+str(result[0])+'\n')
                        
                if predicationLabel in '1' and predicationLabel in  groundTruthLabel:
                    with open('./data/'+bug+'/CorrectPositivePrediction.csv','a') as pred:
                        pred.write(text+'\t'+str(result[0])+'\n')
                    
                    
                    
                    
                    