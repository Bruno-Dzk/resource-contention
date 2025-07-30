import http from "k6/http"
import exec from "k6/execution"

export const options = {
    discardResponseBodies: true,
    scenarios: {
        load_test_1: {
            executor: 'shared-iterations',
            vus: 1000,
            iterations: 1_000_000, 
            maxDuration: '60s',
        }
    },
    tags: {
        id: ""
    }
}

export default function() {
    const {id} = options.tags;
    if (id === "") {
        exec.test.abort("ID tag is missing");
    }
    http.get(`http://139.63.80.70:30123/query/${id}`)
}