/** Русские подписи для машинных статусов backend. */

export const negotiationStageLabels = {
  new: 'Новый',
  need_first_contact: 'Нужен первый контакт',
  waiting_reply: 'Ждём ответ',
  qualified: 'Квалифицирован',
  bargain_started: 'Идёт торг',
  human_review: 'На проверке менеджера',
  offer_ready: 'Оффер готов',
  archived: 'В архиве'
}

export const listingStatusLabels = {
  new: 'Новый',
  scored: 'Оценён',
  shortlisted: 'В шорт-листе',
  human_review: 'На проверке',
  archived: 'В архиве',
  rejected: 'Отклонён'
}

export const negotiationActionLabels = {
  start: 'Старт работы по лоту',
  send_first_message: 'Отправлено первое сообщение',
  incoming_message: 'Получен ответ продавца',
  start_bargain: 'Начат торг',
  prepare_offer: 'Подготовлен оффер',
  archive: 'Диалог архивирован',
  manager_resume: 'Менеджер вернул в работу',
  manager_escalate: 'Ручная эскалация менеджера'
}

export const dealStageLabels = {
  lead: 'Лид',
  qualification: 'Квалификация',
  due_diligence: 'Проверка',
  offer: 'Оффер',
  contract: 'Договор',
  won: 'Выиграна',
  lost: 'Потеряна'
}

/** Возвращает русскую подпись либо исходное значение, если её нет в словаре. */
export function label(dictionary, value) {
  if (!value) return '—'
  return dictionary[value] || value
}
