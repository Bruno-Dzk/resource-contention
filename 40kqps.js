import http from "k6/http"
// import exec from "k6/execution"

export const options = {
    discardResponseBodies: true,
    scenarios: {
        load_test_1: {
            executor: 'constant-arrival-rate',
            rate: 40000,
            timeUnit: '1s',
            duration: '60m',
            preAllocatedVUs: 1000,
            maxVUs: 2000
        }
    },
    // tags: {
    //     id: ""
    // }
}

export default function() {
    // const {id} = options.tags;
    // if (id === "") {
    //     exec.test.abort("ID tag is missing");
    // }
    http.get("http://localhost:3004/query/test")
}