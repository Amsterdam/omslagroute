'use strict';

import { createApp } from 'vue'
import CaseStatus from "./vue/CaseStatus.vue";
import CaseDossierNr from "./vue/CaseDossierNr.vue";
import axios from "axios";

const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value');

axios.defaults.headers.post['X-CSRFToken'] = csrfToken;
axios.defaults.headers.put['X-CSRFToken'] = csrfToken;
axios.defaults.headers.delete['X-CSRFToken'] = csrfToken;

createApp(CaseStatus)
  .mount("#app")

if (!document.querySelector('[data-deny-dossier_nr]')){
  createApp(CaseDossierNr)
    .mount("#dossier_nr")
}