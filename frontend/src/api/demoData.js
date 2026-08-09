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
