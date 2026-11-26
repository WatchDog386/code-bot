/** Print one valid example menu category payload as JSON. */
import { sampleMenuCategory } from "./services";

console.log(JSON.stringify(sampleMenuCategory(1), null, 2));
