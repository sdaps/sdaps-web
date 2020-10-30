import type { QuestionnaireObject } from "./questionnaire";

// TODO: Maybe integrate later
const DEFAULTS = {
  // choiceitem: { answer: "Item", colspan: 1 },
  // choiceitemtext: { answer: "Item", colspan: 2, height: 1.2 },
  // markline: { question: "Question", lower: "a", upper: "b" },
  // groupaddchoice: { choice: "Choice" },
  // choiceline: { question: "question" },
};

export function createQuestionnaireObject(type: QuestionnaireObject["type"], id: number): QuestionnaireObject {
  let res;

  if (type == "multicol") {
    res = { columns: 2 };
  }
  else if (type == "section") {
    res = { title: "Title" }
  }
  else if (type == "textbody") {
    res = { text: "Text" }
  }
  else if (type == "singlemark") {
    res = {
      question: "question",
      checkboxcount: 5,
      lower: "a",
      upper: "b",
    }
  }
  else if (type == "choicequestion") {
    res = { question: "Question", columns: 4 }
  }
  else if (type == "markgroup") {
    res = { heading: "Headline", checkboxcount: 5 }
  }
  else if (type == "choicegroup") {
    res = { heading: "Headline" }
  }
  else if (type == "textbox") {
    res = { question: "Question", height: 4.0, expand: true }
  }

  return { ...res, type, id }
}
