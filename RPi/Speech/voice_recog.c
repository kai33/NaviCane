#include <pocketsphinx.h>
// gcc -o voice_recog voice_recognition.c -DMODELDIR=\"`pkg-config --variable=modeldir pocketsphinx`\" `pkg-config --cflags --libs pocketsphinx sphinxbase`
// somehow the function here is not working well, cannot recognize the correct command
// also this requires dict and lm file to be at usr/share/local/pocketsphinx/model/ folder

int main(int argc, char *argv[]) {
    ps_decoder_t *ps;
    cmd_ln_t *config;
    FILE *fh;
    char const *hyp, *uttid;
    int16 buf[512];
    int rv;
    int32 score;
    
    /* Initializing of the configuration */
    config = cmd_ln_init(NULL, ps_args(), TRUE, 
        "-lm", MODELDIR "/dictionary.lm", "-dict", MODELDIR "/dictionary.dic", NULL);
    ps = ps_init(config);
    
    /* Open audio file and start feeding it into the decoder */
    fh = fopen("recording.wav", "rb");
    rv = ps_start_utt(ps, "hello");
    while (!feof(fh)) {
        size_t nsamp;
        nsamp = fread(buf, 2, 512, fh);
        rv = ps_process_raw(ps, buf, nsamp, FALSE, FALSE);
    }
    rv = ps_end_utt(ps);
    
    /* Get the result and print it */
    hyp = ps_get_hyp(ps, &score, &uttid);
    if (hyp == NULL) {
        exit(1);
    }
    printf("Recognized: %s with prob %d\n", hyp, ps_get_prob (ps, NULL));
    
    /* Free the stuff */
    fclose(fh);
    ps_free(ps);
    return 0;
}
