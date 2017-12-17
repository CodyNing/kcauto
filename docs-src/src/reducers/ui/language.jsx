import * as types from 'types/'

export const language = (state = 'en', action) => {
  switch (action.type) {
    case types.SET_UI_LANGUAGE:
      return action.language
    default:
      return state
  }
}
