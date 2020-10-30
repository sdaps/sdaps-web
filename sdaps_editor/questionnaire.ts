export class Questionnaire extends Array<QuestionnaireObject> {
  getHighestKey(): number {
    return (
      this.reduce((key, section) => Math.max(key, section.id), 0) + 1
    );
  }
}

// TODO: Maybe integrate later
const defaults = {
  multicol: { columns: 2 },
  section: { title: "Title" },
  textbody: { text: "Text" },
  singlemark: {
    question: "question",
    checkboxcount: 5,
    lower: "a",
    upper: "b",
  },
  choicequestion: { question: "Question", columns: 4 },
  markgroup: { heading: "Headline", checkboxcount: 5 },
  choicegroup: { heading: "Headline" },
  textbox: { question: "Question", height: 4.0, expand: true },
  choiceitem: { answer: "Item", colspan: 1 },
  choiceitemtext: { answer: "Item", colspan: 2, height: 1.2 },
  markline: { question: "Question", lower: "a", upper: "b" },
  groupaddchoice: { choice: "Choice" },
  choiceline: { question: "question" },
};

//
export type QuestionnaireObject =
  | SectionQuestionnaireObject
  | MulticolQuestionnaireObject
  | TextbodyQuestionnaireObject
  | SinglemarkQuestionnaireObject
  | TextboxQuestionnaireObject
  | MarkgroupQuestionnaireObject
  | ChoicegroupQuestionnaireObject
  | ChoicequestionQuestionnaireObject;

//
export interface OrderedObject {
  id?: number;
  type: string;
}

//
export interface SectionQuestionnaireObject extends OrderedObject {
  type: "section";
  title: string;
}

//
export interface MulticolQuestionnaireObject extends OrderedObject {
  type: "multicol";
  columns: 1 | 2 | 3 | 4;
  children: Array<MulticolChild>;
}
export type MulticolChild = Exclude<
  QuestionnaireObject,
  MulticolQuestionnaireObject
>;

//
export interface TextbodyQuestionnaireObject extends OrderedObject {
  type: "textbody";
  text: string;
}

//
export interface SinglemarkQuestionnaireObject extends OrderedObject {
  type: "singlemark";
  checkboxcount: number;
  question: string;
  lower: string;
  upper: string;
}

//
export interface TextboxQuestionnaireObject extends OrderedObject {
  type: "textbox";
  expand: boolean;
  height: number;
  question: string;
}

//
export interface MarkgroupQuestionnaireObject extends OrderedObject {
  type: "markgroup";
  heading: string;
  checkboxcount: number;
  children: Array<InnerMarklineQuestionnaireObject>;
}
export interface InnerMarklineQuestionnaireObject extends OrderedObject {
  type: "markline";
  question: string;
  upper: string;
  lower: string;
}

//
export interface ChoicegroupQuestionnaireObject extends OrderedObject {
  type: "choicegroup";
  heading: string;
  children: Array<InnerGroupAddChoice | InnerChoiceLine>;
}
export interface InnerGroupAddChoice extends OrderedObject {
  type: "groupaddchoice";
  choice: string;
}
export interface InnerChoiceLine {
  type: "choiceline";
  question: string;
}

//
export interface ChoicequestionQuestionnaireObject extends OrderedObject {
  type: "choicequestion";
  columns: number;
  question: string;
  children: Array<InnerChoiceAnswer | InnerChoiceTextAnswer>;
}
export interface InnerChoiceAnswer extends OrderedObject {
  type: "choiceitem";
  colspan: number;
  answer: string;
}
export interface InnerChoiceTextAnswer extends OrderedObject {
  type: "choiceitemtext";
  colspan: number;
  answer: string;
  height: number;
}
