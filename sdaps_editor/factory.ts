import type {
  QuestionnaireObject,
  MulticolQuestionnaireObject,
  SectionQuestionnaireObject,
  TextbodyQuestionnaireObject,
  SinglemarkQuestionnaireObject,
  TextboxQuestionnaireObject,
  MarkgroupQuestionnaireObject,
  ChoicegroupQuestionnaireObject,
  ChoicequestionQuestionnaireObject,
} from "./questionnaire";

export function createQuestionnaireObject(
  type: "section",
  id: number
): SectionQuestionnaireObject;
export function createQuestionnaireObject(
  type: "textbody",
  id: number
): TextbodyQuestionnaireObject;
export function createQuestionnaireObject(
  type: "singlemark",
  id: number
): SinglemarkQuestionnaireObject;
export function createQuestionnaireObject(
  type: "textbox",
  id: number
): TextboxQuestionnaireObject;
export function createQuestionnaireObject(
  type: "markgroup",
  id: number
): MarkgroupQuestionnaireObject;
export function createQuestionnaireObject(
  type: "choicegroup",
  id: number
): ChoicegroupQuestionnaireObject;
export function createQuestionnaireObject(
  type: "choicequestion",
  id: number
): ChoicequestionQuestionnaireObject;
export function createQuestionnaireObject(
  type: QuestionnaireObject["type"],
  id: number
) {
  if (type === "multicol") {
    return { type, id, columns: 2, children: [] };
  } else if (type === "section") {
    return { type, id, title: "Title" };
  } else if (type === "textbody") {
    return { type, id, text: "Text" };
  } else if (type === "singlemark") {
    return {
      type,
      id,
      question: "question",
      checkboxcount: 5,
      lower: "a",
      upper: "b",
    };
  } else if (type === "choicequestion") {
    return { type, id, question: "Question", columns: 4, children: [] };
  } else if (type === "markgroup") {
    return { type, id, heading: "Headline", checkboxcount: 5, children: [] };
  } else if (type === "choicegroup") {
    return { type, id, heading: "Headline", children: [] };
  } else if (type === "textbox") {
    return { type, id, question: "Question", height: 4.0, expand: true };
  }
}
