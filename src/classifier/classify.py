import lstm
import classifier_preprocess
import cPickle
import logisticregression as lr
from gensim.models.keyedvectors import KeyedVectors
from keras.preprocessing.sequence import pad_sequences

class Classify(object):
    def __init__(self):
        self.bd=classifier_preprocess.ClassifierPreProcess()
        self.tl=lstm.TopicLSTM()
        self.lc=lr.LogisticClassifier()
        self.bd.w2v_model=KeyedVectors.load_word2vec_format('../GoogleNews-vectors-negative300.bin', binary=True)
        self.lc.ids_answer=None
    def create_data(self):
        print "Building dataset..."
        print "Reading topics..."
        self.bd.read_topics()
        print "Reading data..."
        self.bd.read_data()
        print "Generate w2v vectors..."
        self.bd.generate_training_vectors()
        self.bd.generate_sparse_topic_vectors()
        print "write data..."
        self.bd.write_data()

    def train_lstm(self):
        print "Starting LSTM topic training..."
        print "LSTM is reading training data..."
        self.tl.read_training_data()
        print "Training LSTM..."
        self.tl.train_lstm()
        print "Trained LSTM."

    def train_lr(self,method='fused'):
        self.lc.ids_answer=cPickle.load(open('train_data/ids_answer.pkl','rb'))
        print "Starting LR training..."
        print "LR is reading training data..."
        self.lc.load_data()
        self.lc.create_vectors(method)
        print "Training LR..."
        self.lc.train_lr(method)
        print "Trained LR"
        y_test, y_pred = self.lc.test_lr(method)
        return y_test, y_pred

    def get_answer(self,question):
        processed_question=self.bd.preprocessor.transform(question)
        w2v_vector, lstm_vector=self.bd.get_w2v(processed_question)
        lstm_vector=[lstm_vector]
        padded_vector=pad_sequences(lstm_vector,maxlen=25, dtype='float32',padding='post',truncating='post',value=0.)
        topic_vector=self.tl.get_topic_vector(padded_vector)
        predicted_answer=self.lc.get_prediction(w2v_vector, topic_vector)
        return predicted_answer



# def main():
#     classifier=Classify()
#     #classifier.create_data()
#     #classifier.train_lstm()
#     y_test, y_pred=classifier.train_lr()
#     print "You can ask questions now. Type 'exit' to exit"
#     question=raw_input("Guest: ") #fetch after each space?
#     while question!= 'exit':
#         answer=classifier.get_answer(question)
#         print "Clint: ",
#         print answer
#         print "\n"
#         question=raw_input("Guest: ")

# if __name__=='__main__':
#     main()
