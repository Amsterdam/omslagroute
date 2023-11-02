<template>
    <div>
        <header>
            <h2 class="h3 u-margin-top-none">Status aanvraag</h2>
        </header>
        <div class="status--wrapper">
            <div>
                <span v-html="getSvg(currentCaseStatus.status)" v-bind:class="setHistoryClass(currentCaseStatus.status)"></span>
                <span>{{ caseStatusPrefix }}{{ caseStatusOptions[currentCaseStatus.status].current }}</span>
                <div class="status-container">
                    <div class="facts">
                        <small>{{ currentCaseStatus.created | moment("DD-MM-YYYY HH:mm") }} </small><small class="u-float-right">{{ currentCaseStatus.username }}</small>
                        <p>{{ currentCaseStatus.status_comment}}</p>
                    </div>
                </div>

            </div>
            <div class="form-field u-margin-bottom-none screen-only">
                <button v-for="(value, id) in currentCaseStatusOptions" v-bind:key="id" v-on:click="setNextStatus(id)"  v-bind:class="setButtonClass(id)">
                    <span v-html="getSvg(id)"></span>
                    {{ value.verb }}
                </button>
            </div>

            <div v-if="nextCaseStatus.status" class="container-modal--vue">
                <a href="#" class="modal-close--bg" v-on:click="setNextStatus(null)" ></a>
                <div class="prompt-container show-prompt-approve" data-handler="prompt-approve">
                    <button v-on:click="setNextStatus(null)" class="button button--close">
                        <svg width="20" height="20" title="Sluit venster">
                            <use href="#close" xlink:href="#close" width="20" height="20"></use>
                        </svg>
                        <span class="sr-only">Sluit venster</span>
                    </button>
                    <h2>Status wijzigen</h2>
                    <div class="prompt-approve">
                        <p>Weet je zeker dat je de status voor <strong>{{ title }}</strong> wilt wijzigen naar <strong>{{ caseStatusOptions[nextCaseStatus.status].verb }}</strong>?</p>
                        <p v-if="emailList"><strong>{{ emailList }}</strong> ontvangt hiervan een bevestiging per e-mail.</p>
                        <form>
                            <div class="form-field form-field--textarea screen-only u-margin-top-2x">
                                <label for="status-message">Bericht (optioneel)</label>
                                <textarea v-model="nextCaseStatus.status_comment" id="status-message" name="status-message" cols="40" rows="4"></textarea>
                            </div>
                            <span class="helptext">Als je een bericht wil meesturen met in de bevestings e-mail, dan kun je dat hier doen.</span>
                            <div class="form-field form-field--buttons screen-only u-margin-top-2x">
                                <button type="button" class="button button--secondary" v-on:click="setNextStatus(null)" data-handler="modal-close">Annuleren</button>
                                <button type="button" class="button button--primary"  v-on:click="addCaseStatus()">{{ getButtonText(nextCaseStatus.status) }}</button>
                            </div>
                        </form>
                    </div>

                </div>
            </div>
            <div class="status-history-container form-field-history screen-only">
                <details>
                    <summary>Historie<svg class="icon-details--closed" width="14" height="9">
                            <use href="#chevron-down" xlink:href="#chevron-down" width="14" height="9"></use>
                        </svg><svg class="icon-details--open" width="14" height="9">
                            <use href="#chevron-up" xlink:href="#chevron-up" width="14" height="9"></use>
                        </svg>
                    </summary>
                    <div class="content">
                        <button type="button" data-handler="close-details" class="button button--close">
                            <span class="sr-only">Verberg historie</span>
                            <svg class="icon close__icon" width="12" height="12">
                                <use href="#close" xlink:href="#close" width="12" height="12"></use>
                            </svg>
                        </button>
                        <div class="u-scroll-wrapper">
                            <ul class="u-list-style-none">
                                <li v-for="h in statusHistory" :key="h.id">
                                    <span v-html="getSvg(h.status)" v-bind:class="setHistoryClass(h.status)"></span>
                                    <small class="status">{{caseStatusOptions[h.status].current }}</small>
                                    <div class="facts">
                                        <div class="u-clearfix">
                                            <small>{{ h.created | moment("DD-MM-YYYY HH:mm") }} </small><small class="u-float-right">{{ h.username }}</small>
                                        </div>
                                        <p>{{ h.status_comment}}</p>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </details>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {

// CASE_STATUS_INGEDIEND = 1
// CASE_STATUS_AFGEKEURD = 2
// CASE_STATUS_GOEDGEKEURD = 3
// CASE_STATUS_IN_BEHANDELING = 4
// CASE_STATUS_WONINGCORPORATIE_INGEDIEND = 5
// CASE_STATUS_WONINGCORPORATIE_AFGEKEURD = 6
// CASE_STATUS_WONINGCORPORATIE_GOEDGEKEURD = 7
// CASE_STATUS_WONINGCORPORATIE_IN_BEHANDELING = 8
    name: "CaseStatus",
    data: () => ({
        loading: false,
        currentCaseStatus: {'status': 1},
        nextCaseStatus: {
            'status': 0,
            'form': null,
            'case': null,
            'status_comment': null,
            'caseversion': null,
        },
        statusHistory: [],
        caseStatusOptions: {},
        currentCaseStatusOptions: {},
        caseStatusIds: [],
        caseStatusPrefix: '',
        title: null,
        caseId: null,
        form: null,
        message: null,
        emailList: null,

        buttonClass: {
            2: "u-margin-bottom u-margin-right button button--danger",
            3: "u-margin-bottom u-margin-right button button--success",
            4: "u-margin-bottom u-margin-right button button--warning",
            6: "u-margin-bottom u-margin-right button button--danger",
            7: "u-margin-bottom u-margin-right button button--success",
            8: "u-margin-bottom u-margin-right button button--warning",
        },
        historyClass: {
            2: "icon-circle icon-circle--status-disapproved",
            3: "icon-circle icon-circle--status-approved",
            4: "icon-circle icon-circle--status-pending",
            6: "icon-circle icon-circle--status-disapproved",
            7: "icon-circle icon-circle--status-approved",
            8: "icon-circle icon-circle--status-pending",
        },
        svg: {
            2: '<svg class="icon close__icon" width="14" height="14"><use href="#close" xlink:href="#close" width="14" height="14"></use></svg>',
            3: '<svg class="icon check__icon" width="20" height="16"><use href="#check" xlink:href="#check" width="20" height="18"></use></svg>',
            4: '<svg class="icon pause__icon" width="12" height="16"><use href="#pause" xlink:href="#pause" width="12" height="16"></use></svg>',
            6: '<svg class="icon close__icon" width="14" height="14"><use href="#close" xlink:href="#close" width="14" height="14"></use></svg>',
            7: '<svg class="icon check__icon" width="20" height="16"><use href="#check" xlink:href="#check" width="20" height="18"></use></svg>',
            8: '<svg class="icon pause__icon" width="12" height="16"><use href="#pause" xlink:href="#pause" width="12" height="16"></use></svg>',
        },
    }),
    computed: {
    },
    beforeMount(){
        this.getCaseStatusList();
        this.currentCaseStatusOptions = this.getCaseStatusOptions();
    },
    created() {
        this.getInitialData();
    },
    methods: {
        getCaseStatusOptions(){
            return Object.keys(this.caseStatusOptions).reduce((a, b, c) => {
                if (b !== '1' && b !== String(this.currentCaseStatus.status)){
                    a[b] = this.caseStatusOptions[b];
                }
                return a;
            }, {});
        },
        getSvg: function(status){
            return this.svg[status];
        },
        getButtonText: function(status){
            return 'Aanvraag ' + this.caseStatusOptions[status].verb.toLowerCase();
        },
        setHistoryClass: function(status){
            return this.historyClass[status];
        },
        setButtonClass: function(status){
            return (this.buttonClass[status] + (this._data.currentCaseStatus.status !== 1 ? ' button--secondary': ''));
        },
        setNextStatus: function(status){
            this.nextCaseStatus.status = status;
        },
        getInitialData: function(){
            this.caseId = document.querySelector('[data-case-id]').dataset.caseId;
            this.form = document.querySelector('[data-form]').dataset.form;
            this.title = document.querySelector('[data-title]').dataset.title;
            this.emailList = document.querySelector('[data-email-list]').dataset.emailList;
            this.caseStatusOptions = JSON.parse(document.querySelector('[data-case-status-options]').dataset.caseStatusOptions);
            this.caseStatusIds = Object.keys(this.caseStatusOptions).join('&status=');
            this.nextCaseStatus.case = this.caseId;
            this.nextCaseStatus.form = this.form;
        },
        getCaseStatusList: function () {
            this.loading = true;
            this.nextCaseStatus.status = null;
            axios.get(`/api/casestatus/?case=${this.caseId}&form=${this.form}&status=${this.caseStatusIds}`)
                .then((response) => {
                    let filtered = response.data.results
                    if (filtered.length > 1 && filtered[0].status === 1){
                        this.caseStatusPrefix = 'Opnieuw ';
                    }
                    this.currentCaseStatus = filtered[0] || {'status': 1};
                    this.currentCaseStatusOptions = this.getCaseStatusOptions();
                    filtered.shift();
                    this.statusHistory = filtered;
                    this.loading = false;
                })
                .catch((err) => {
                    this.loading = false;
                    console.log(err);
                })
        },
        addCaseStatus: function () {
            this.loading = true;
            axios.post(`/api/casestatus/`, this.nextCaseStatus)
                .then((response) => {
                    this.loading = false;
                    this.caseStatusPrefix = '';
                    this.nextCaseStatus.status_comment = null;
                    this.getCaseStatusList();
                })
                .catch((err) => {
                    this.loading = false;
                    console.log(err);
                })
        },
    }
};
</script>

<style lang="css">

</style>