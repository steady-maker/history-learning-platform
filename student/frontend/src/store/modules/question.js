export const useQuestionStore = defineStore('question', {
  state: () => ({
    currentQuestion: null, // 存储当前要做的题目对象
  }),
  actions: {
    // 设置题目对象
    setCurrentQuestion(question) {
      this.currentQuestion = question
    },
    // 清空题目（避免残留）
    clearCurrentQuestion() {
      this.currentQuestion = null
    }
  },
})