/** Print one valid example venue payload as JSON. */
import { sampleVenue } from "./services";

console.log(JSON.stringify(sampleVenue(1), null, 2));
