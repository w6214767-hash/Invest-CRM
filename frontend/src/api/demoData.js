/**
 * Демонстрационные данные для витрины интерфейса без backend.
 *
 * Используются только когда сборка запущена с VITE_DEMO_MODE=1.
 * Цифры условные и нужны, чтобы показать логику скоринга и воронки.
 */

export const demoListings = [
  {
    id: 1,
    title: 'Участок 12 сот., ИЖС, Домодедово, д. Шишкино',
    region: 'Московская область',
    district: 'Домодедово',
    area_sotka: 12,
    price_rub: 3150000,
    price_per_sotka: 262500,
    discount_pct: 21.4,
    score: 78.4,
    status: 'scored',
    negotiation_stage: 'bargain_started',
    cadastral_number: '50:28:0050201:412',
    description:
      'Срочно продаём участок ИЖС 12 соток. Свет по границе, газ в 80 м, круглогодичный подъезд, асфальт. Межевание сделано, собственность более 3 лет. Возможен торг при быстром выходе на сделку.',
    red_flags: []
  },
  {
    id: 2,
    title: 'Участок 8 сот., СНТ «Барыбино-2», Домодедово',
    region: 'Московская область',
    district: 'Домодедово',
    area_sotka: 8,
    price_rub: 1450000,
    price_per_sotka: 181250,
    discount_pct: 17.8,
    score: 71.2,
    status: 'scored',
    negotiation_stage: 'qualified',
    cadastral_number: '50:28:0060118:77',
    description:
      'Участок в СНТ, электричество 15 кВт подключено, скважина. Нужны деньги на переезд, торг уместен. Подъезд грунтовый, зимой чистят.',
    red_flags: ['Неподтверждённые коммуникации']
  },
  {
    id: 3,
    title: 'Участок 15 сот., ИЖС, Ступино, с. Малино',
    region: 'Московская область',
    district: 'Ступино',
    area_sotka: 15,
    price_rub: 2700000,
    price_per_sotka: 180000,
    discount_pct: 14.3,
    score: 64.8,
    status: 'scored',
    negotiation_stage: 'waiting_reply',
    cadastral_number: '50:33:0030214:118',
    description:
      'Ровный прямоугольный участок, фасад 30 м. Электричество по границе, газ в перспективе. Документы в порядке, один собственник.',
    red_flags: ['Неподтверждённые коммуникации']
  },
  {
    id: 4,
    title: 'Участок 20 сот., ЛПХ, Чехов, д. Мещерское',
    region: 'Московская область',
    district: 'Чехов',
    area_sotka: 20,
    price_rub: 4600000,
    price_per_sotka: 230000,
    discount_pct: 9.1,
    score: 52.6,
    status: 'scored',
    negotiation_stage: 'need_first_contact',
    cadastral_number: '50:31:0040507:203',
    description:
      'Большой участок под строительство дома или два дома под раздел. Свет 15 кВт, газ по улице. Продажа не срочная, цену держим.',
    red_flags: []
  },
  {
    id: 5,
    title: 'Участок 10 сот., Домодедово, мкр. Востряково',
    region: 'Московская область',
    district: 'Домодедово',
    area_sotka: 10,
    price_rub: 2200000,
    price_per_sotka: 220000,
    discount_pct: 26.7,
    score: 49.3,
    status: 'human_review',
    negotiation_stage: 'human_review',
    cadastral_number: null,
    description:
      'Продажа по расписке, документы оформляются. Цена ниже рынка, срочно. Участок без обременений со слов собственника.',
    red_flags: [
      'Сомнительный статус документов',
      'Не указан кадастровый номер'
    ]
  },
  {
    id: 6,
    title: 'Участок 6 сот., СНТ «Заря», Домодедово',
    region: 'Московская область',
    district: 'Домодедово',
    area_sotka: 6,
    price_rub: 980000,
    price_per_sotka: 163333,
    discount_pct: 11.2,
    score: 44.1,
    status: 'new',
    negotiation_stage: 'new',
    cadastral_number: '50:28:0070911:34',
    description:
      'Небольшой участок под дачу. Свет рядом, воды нет. Подъезд грунтовый, весной размывает.',
    red_flags: ['Неподтверждённые коммуникации']
  },
  {
    id: 7,
    title: 'Участок 14 сот., ИЖС, Раменское, с. Никоновское',
    region: 'Московская область',
    district: 'Раменское',
    area_sotka: 14,
    price_rub: 3080000,
    price_per_sotka: 220000,
    discount_pct: 18.5,
    score: 73.9,
    status: 'scored',
    negotiation_stage: 'offer_ready',
    cadastral_number: '50:23:0020604:59',
    description:
      'Собственник готов к быстрому выходу на сделку, есть аванс от нас. Все коммуникации по границе, категория земель — земли населённых пунктов, ИЖС. Торг обсуждаем.',
    red_flags: []
  },
  {
    id: 8,
    title: 'Участок 9 сот., Подольск, д. Сынково',
    region: 'Московская область',
    district: 'Подольск',
    area_sotka: 9,
    price_rub: 2790000,
    price_per_sotka: 310000,
    discount_pct: 4.6,
    score: 33.7,
    status: 'archived',
    negotiation_stage: 'archived',
    cadastral_number: '50:27:0030412:88',
    description:
      'Хорошая локация рядом с трассой, но цена близка к рынку. Продавец на торг не идёт.',
    red_flags: []
  }
]

export const demoDeals = [
  { id: 101, listing_id: 1, stage: 'offer', amount_rub: 2850000, manager_name: 'Владимир Денисов' },
  { id: 102, listing_id: 7, stage: 'due_diligence', amount_rub: 2900000, manager_name: 'Анна Кузьмина' },
  { id: 103, listing_id: 2, stage: 'qualification', amount_rub: 1300000, manager_name: 'Анна Кузьмина' },
  { id: 104, listing_id: 3, stage: 'lead', amount_rub: null, manager_name: null },
  { id: 105, listing_id: 4, stage: 'contract', amount_rub: 4400000, manager_name: 'Владимир Денисов' },
  { id: 106, listing_id: 8, stage: 'lost', amount_rub: null, manager_name: 'Владимир Денисов' }
]

export const demoDashboard = {
  leads_count: demoListings.length,
  conversion_pct: 25.0,
  average_discount_pct: 15.5,
  active_deals_count: 5
}

const demoScriptTemplates = {
  first_contact: 'Здравствуйте! Подскажите, пожалуйста, участок ещё актуален? Если да, удобно ли сегодня коротко уточнить детали и договориться о просмотре?',
  facts: 'Спасибо. Чтобы подготовиться к просмотру, уточните, пожалуйста: как оформлены коммуникации, какой подъезд к участку зимой, есть ли обременения и завершено ли межевание?',
  motivation: 'Подскажите, пожалуйста, насколько срочна продажа и что для вас важно по срокам выхода на сделку? Рассматриваете быстрый задаток при понятных условиях?',
  bargain_test: 'Если по документам всё в порядке и мы сможем быстро согласовать задаток, готовы ли вы обсудить цену? Какой минимум для вас был бы предметом разговора?'
}

const demoEvents = {
  1: [
    { id: 101, from_stage: 'new', to_stage: 'need_first_contact', reason: 'start', actor: 'система', escalation_reasons: [], created_at: '2026-08-08T08:50:00' },
    { id: 102, from_stage: 'need_first_contact', to_stage: 'waiting_reply', reason: 'send_first_message', actor: 'агент', escalation_reasons: [], created_at: '2026-08-08T09:00:00' },
    { id: 103, from_stage: 'waiting_reply', to_stage: 'qualified', reason: 'incoming_message', actor: 'система', escalation_reasons: [], created_at: '2026-08-08T10:12:00' },
    { id: 104, from_stage: 'qualified', to_stage: 'bargain_started', reason: 'start_bargain', actor: 'Анна Кузьмина', escalation_reasons: [], created_at: '2026-08-09T09:20:00' }
  ],
  2: [
    { id: 201, from_stage: 'new', to_stage: 'need_first_contact', reason: 'start', actor: 'система', escalation_reasons: [], created_at: '2026-08-07T10:00:00' },
    { id: 202, from_stage: 'need_first_contact', to_stage: 'waiting_reply', reason: 'send_first_message', actor: 'агент', escalation_reasons: [], created_at: '2026-08-07T10:04:00' },
    { id: 203, from_stage: 'waiting_reply', to_stage: 'qualified', reason: 'incoming_message', actor: 'система', escalation_reasons: [], created_at: '2026-08-07T12:18:00' }
  ],
  3: [
    { id: 301, from_stage: 'new', to_stage: 'need_first_contact', reason: 'start', actor: 'система', escalation_reasons: [], created_at: '2026-08-09T08:31:00' },
    { id: 302, from_stage: 'need_first_contact', to_stage: 'waiting_reply', reason: 'send_first_message', actor: 'агент', escalation_reasons: [], created_at: '2026-08-09T08:40:00' }
  ],
  5: [
    { id: 501, from_stage: 'new', to_stage: 'need_first_contact', reason: 'start', actor: 'система', escalation_reasons: [], created_at: '2026-08-08T11:10:00' },
    { id: 502, from_stage: 'need_first_contact', to_stage: 'waiting_reply', reason: 'send_first_message', actor: 'агент', escalation_reasons: [], created_at: '2026-08-08T11:14:00' },
    { id: 503, from_stage: 'waiting_reply', to_stage: 'human_review', reason: 'incoming_message', actor: 'система', escalation_reasons: ['Обсуждается кадастровый номер', 'Обнаружен юридический риск'], created_at: '2026-08-08T13:42:00' }
  ],
  7: [
    { id: 701, from_stage: 'new', to_stage: 'need_first_contact', reason: 'start', actor: 'система', escalation_reasons: [], created_at: '2026-08-06T09:10:00' },
    { id: 702, from_stage: 'need_first_contact', to_stage: 'waiting_reply', reason: 'send_first_message', actor: 'агент', escalation_reasons: [], created_at: '2026-08-06T09:15:00' },
    { id: 703, from_stage: 'waiting_reply', to_stage: 'qualified', reason: 'incoming_message', actor: 'система', escalation_reasons: [], created_at: '2026-08-06T11:05:00' },
    { id: 704, from_stage: 'qualified', to_stage: 'offer_ready', reason: 'prepare_offer', actor: 'Анна Кузьмина', escalation_reasons: [], created_at: '2026-08-09T11:38:00' }
  ]
}

export const demoNegotiations = [
  {
    listing_id: 1,
    seller: { name: 'Сергей', seller_type: 'owner', urgency_score: 82 },
    stage: 'bargain_started',
    allowed_next_actions: ['offer_ready', 'human_review', 'archived'],
    escalated: false,
    escalation_reasons: [],
    events: demoEvents[1],
    messages: [
      { id: 1001, direction: 'out', body: 'Здравствуйте! Подскажите, участок в Шишкино ещё продаётся?', sent_at: '2026-08-08T09:00:00', sent_by_human: false, is_draft: true },
      { id: 1002, direction: 'in', body: 'Добрый день. Да, актуален, собственник я. Показать могу в выходные.', sent_at: '2026-08-08T10:12:00', sent_by_human: false, is_read: true },
      { id: 1003, direction: 'out', body: 'Спасибо. Электричество и газ подтверждены документами? Межевание уже сделано?', sent_at: '2026-08-08T10:25:00', sent_by_human: false },
      { id: 1004, direction: 'in', body: 'Свет 15 кВт по границе, договор с Мособлэнерго есть. Газ по улице, межевой план на руках. Подъезд асфальт, зимой чистят.', sent_at: '2026-08-08T11:06:00', sent_by_human: false, is_read: true },
      { id: 1005, direction: 'out', body: 'Условия понятны. При быстром задатке и проверке документов готовы рассмотреть 2,85 млн?', sent_at: '2026-08-09T09:24:00', sent_by_human: true },
      { id: 1006, direction: 'in', body: 'Ниже 2,9 млн не хотелось бы. Если без долгих согласований, могу уступить до этой суммы.', sent_at: '2026-08-09T09:48:00', sent_by_human: false, is_read: false },
      { id: 1007, direction: 'out', body: 'Поняла, 2,9 млн зафиксировала. Проверим пакет и вернёмся сегодня по сроку задатка.', sent_at: '2026-08-09T10:06:00', sent_by_human: true }
    ]
  },
  {
    listing_id: 2,
    seller: { name: 'Елена', seller_type: 'owner', urgency_score: 74 },
    stage: 'qualified',
    allowed_next_actions: ['bargain_started', 'offer_ready', 'human_review', 'archived'],
    escalated: false,
    escalation_reasons: [],
    events: demoEvents[2],
    messages: [
      { id: 2001, direction: 'out', body: 'Здравствуйте! Участок в СНТ «Барыбино-2» ещё продаётся?', sent_at: '2026-08-07T10:04:00', sent_by_human: false },
      { id: 2002, direction: 'in', body: 'Да, продаётся. Переезжаем, поэтому хотелось бы решить вопрос в августе.', sent_at: '2026-08-07T12:18:00', sent_by_human: false, is_read: true },
      { id: 2003, direction: 'out', body: 'Спасибо. Скажите, электричество уже подключено, а подъезд зимой проезжаемый?', sent_at: '2026-08-07T12:31:00', sent_by_human: false },
      { id: 2004, direction: 'in', body: '15 кВт подключено, лицевой счёт есть. Дорога грунтовая, СНТ зимой чистит, но после сильного снегопада не сразу.', sent_at: '2026-08-07T13:02:00', sent_by_human: false, is_read: true },
      { id: 2005, direction: 'out', body: 'Хорошо, подготовим вопросы к просмотру и напишем по времени.', sent_at: '2026-08-09T09:12:00', sent_by_human: true }
    ]
  },
  {
    listing_id: 3,
    seller: { name: 'Игорь', seller_type: 'owner', urgency_score: 38 },
    stage: 'waiting_reply',
    allowed_next_actions: ['qualified', 'human_review', 'archived'],
    escalated: false,
    escalation_reasons: [],
    events: demoEvents[3],
    messages: [
      { id: 3001, direction: 'out', body: 'Здравствуйте! Подскажите, участок в Малино ещё актуален и можно ли посмотреть его на неделе?', sent_at: '2026-08-09T08:40:00', sent_by_human: false },
      { id: 3002, direction: 'in', body: 'Добрый день. Актуален, но сегодня занят. Напишите завтра после обеда.', sent_at: '2026-08-09T09:18:00', sent_by_human: false, is_read: true },
      { id: 3003, direction: 'out', body: 'Конечно. Заодно уточним по электричеству, газу и готовности межевого плана.', sent_at: '2026-08-09T09:24:00', sent_by_human: false },
      { id: 3004, direction: 'in', body: 'Договорились, завтра после двух.', sent_at: '2026-08-09T09:27:00', sent_by_human: false, is_read: false }
    ]
  },
  {
    listing_id: 5,
    seller: { name: 'Александр', seller_type: 'unknown', urgency_score: 91 },
    stage: 'human_review',
    allowed_next_actions: ['qualified', 'bargain_started', 'offer_ready', 'archived'],
    escalated: true,
    escalation_reasons: ['Обсуждается кадастровый номер', 'Обнаружен юридический риск'],
    events: demoEvents[5],
    messages: [
      { id: 5001, direction: 'out', body: 'Здравствуйте! Участок в Востряково ещё продаётся? Хотели бы уточнить документы перед просмотром.', sent_at: '2026-08-08T11:14:00', sent_by_human: false },
      { id: 5002, direction: 'in', body: 'Да, срочно. Документы сейчас делаем, пока можно оформить по расписке, так быстрее.', sent_at: '2026-08-08T13:21:00', sent_by_human: false, is_read: true },
      { id: 5003, direction: 'out', body: 'Понял. Пришлите, пожалуйста, кадастровый номер и информацию о межевании, чтобы проверить участок.', sent_at: '2026-08-08T13:29:00', sent_by_human: true },
      { id: 5004, direction: 'in', body: 'Кадастрового пока нет под рукой, границы старые. Но участок мой, расписка надёжная, цену можем обсудить.', sent_at: '2026-08-08T13:42:00', sent_by_human: false, is_read: false },
      { id: 5005, direction: 'out', body: 'Спасибо, передаю вопрос менеджеру по документам. Вернёмся после проверки.', sent_at: '2026-08-08T13:49:00', sent_by_human: true }
    ]
  },
  {
    listing_id: 7,
    seller: { name: 'Наталья', seller_type: 'owner', urgency_score: 88 },
    stage: 'offer_ready',
    allowed_next_actions: ['archived'],
    escalated: false,
    escalation_reasons: [],
    events: demoEvents[7],
    messages: [
      { id: 7001, direction: 'out', body: 'Здравствуйте! Участок в Никоновском ещё продаётся? Интересует быстрый выход на сделку.', sent_at: '2026-08-06T09:15:00', sent_by_human: false },
      { id: 7002, direction: 'in', body: 'Да, актуален. Все документы готовы, один собственник. Можем быстро выйти на сделку.', sent_at: '2026-08-06T11:05:00', sent_by_human: false, is_read: true },
      { id: 7003, direction: 'out', body: 'Отлично. Межевание, коммуникации и подъезд можно подтвердить выпиской и документами?', sent_at: '2026-08-06T11:17:00', sent_by_human: false },
      { id: 7004, direction: 'in', body: 'Да, межевание есть, свет и газ по границе. Выписку и план отправлю при встрече.', sent_at: '2026-08-06T12:01:00', sent_by_human: false, is_read: true },
      { id: 7005, direction: 'out', body: 'Готовим оффер 2,9 млн с задатком в течение трёх дней после проверки пакета. Такой порядок вам подходит?', sent_at: '2026-08-09T11:20:00', sent_by_human: true },
      { id: 7006, direction: 'in', body: 'Подходит. Если задаток без затягивания, готова зафиксировать 2,9 млн.', sent_at: '2026-08-09T11:35:00', sent_by_human: false, is_read: false }
    ]
  }
].map((dialog) => ({
  ...dialog,
  listing: demoListings.find((item) => item.id === dialog.listing_id)
}))

function copy(value) {
  return JSON.parse(JSON.stringify(value))
}

function getDialog(id) {
  const dialog = demoNegotiations.find((item) => String(item.listing_id) === String(id))
  if (!dialog) throw new Error('Переговоры по этому участку не найдены в демо-данных')
  return dialog
}

export function getDemoNegotiations() {
  return demoNegotiations
    .map((dialog) => {
      const lastMessage = dialog.messages.at(-1)
      return {
        listing_id: dialog.listing_id,
        title: dialog.listing.title,
        district: dialog.listing.district || dialog.listing.region,
        price_rub: dialog.listing.price_rub,
        discount_pct: dialog.listing.discount_pct,
        score: dialog.listing.score,
        stage: dialog.stage,
        seller_name: dialog.seller.name,
        last_message: lastMessage ? { body: lastMessage.body, sent_at: lastMessage.sent_at } : null,
        unread_count: dialog.messages.filter((message) => message.direction === 'in' && !message.is_read).length,
        escalated: dialog.escalated
      }
    })
    .sort((first, second) => new Date(second.last_message?.sent_at || 0) - new Date(first.last_message?.sent_at || 0))
}

export function getDemoNegotiation(id) {
  return copy(getDialog(id))
}

export function createDemoDraft(id, intent = 'first_contact') {
  getDialog(id)
  return {
    draft_message: demoScriptTemplates[intent] || demoScriptTemplates.first_contact,
    prompt_used: `Локальный сценарий: ${intent || 'first_contact'}`
  }
}

export function sendDemoMessage(id, body) {
  const dialog = getDialog(id)
  const message = {
    id: Date.now(),
    direction: 'out',
    body: body.trim(),
    sent_at: new Date().toISOString(),
    sent_by_human: true,
    is_read: true
  }
  dialog.messages.push(message)
  return copy(message)
}
