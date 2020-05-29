'use strict';

import Vue from "vue";
import CaseStatus from "./vue/CaseStatus.vue";
import axios from "axios";

const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value');

axios.defaults.headers.post['X-CSRFToken'] = csrfToken;
axios.defaults.headers.put['X-CSRFToken'] = csrfToken;
axios.defaults.headers.delete['X-CSRFToken'] = csrfToken;

new Vue({
 el: "#app",
 render: h => h(CaseStatus)
});